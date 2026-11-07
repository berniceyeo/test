import re

import pytest

from app.errors import ExceedMaxBoardSizeError, InvalidInputError
from app.constants import MAX_BRICKS, MAX_HEIGHT, MAX_WIDTH
from app.controller import parse_to_valid_inputs
from app.main import main
from app.models import Direction


@pytest.mark.parametrize(
    "config",
    ["", "4 5", "abc 5 H@~~", "4 abc H@~~", "0 5 H@~~", "4 -1 H@~~", "4 5 X@~~"],
)
def test_invalid_setup_prompts_again(config, monkeypatch, capsys):
    answers = iter([config, "4 3 H@~~", "D", "Q"])
    prompts = []

    def answer(prompt):
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", answer)
    main()

    assert sum("height" in prompt for prompt in prompts) == 2
    assert "Thank you for playing" in capsys.readouterr().out


def test_parse_valid_configuration():
    config = parse_to_valid_inputs(" 4  5 H@~~ V^** ")
    assert config.width == 4
    assert config.height == 5
    assert [(brick.direction, brick.symbols) for brick in config.bricks] == [
        (Direction.HORIZONTAL, ["@", "~", "~"]),
        (Direction.VERTICAL, ["^", "*", "*"]),
    ]


@pytest.mark.parametrize("config", ["abc 5 H@~~", "4 abc H@~~"])
def test_rejects_non_numeric_board_size_with_friendly_message(config):
    with pytest.raises(
        InvalidInputError,
        match=re.escape("Width and height must be whole numbers."),
    ):
        parse_to_valid_inputs(config)


def test_rejects_configuration_with_more_than_five_bricks():
    config = "4 3 " + " ".join(["H@~~"] * (MAX_BRICKS + 1))

    with pytest.raises(
        InvalidInputError,
        match=re.escape(f"Enter no more than {MAX_BRICKS} bricks."),
    ):
        parse_to_valid_inputs(config)


@pytest.mark.parametrize(
    "config",
    [
        f"{MAX_WIDTH + 1} {MAX_HEIGHT} H@~~",
        f"{MAX_WIDTH} {MAX_HEIGHT + 1} H@~~",
    ],
)
def test_rejects_configuration_larger_than_maximum_board(config):
    with pytest.raises(
        ExceedMaxBoardSizeError,
        match=re.escape(
            f"Board cannot exceed {MAX_WIDTH} columns by {MAX_HEIGHT} rows."
        ),
    ):
        parse_to_valid_inputs(config)


def test_accepts_maximum_board_size():
    config = parse_to_valid_inputs(f"{MAX_WIDTH} {MAX_HEIGHT} H@~~")
    assert config.width == MAX_WIDTH
    assert config.height == MAX_HEIGHT


def test_spawn_failure_offers_restart_and_quit(monkeypatch, capsys):
    # The second brick cannot spawn on a one-row board.
    answers = iter(
        [
            "3 1 H@~~ H^**",
            "D",
            "S",
            "3 1 H@~~ H^**",
            "D",
            "Q",
        ]
    )
    prompts = []

    def answer(prompt):
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", answer)
    main()

    output = capsys.readouterr().out
    assert output.count("Game Over") == 2
    assert sum("height" in prompt for prompt in prompts) == 2
    assert sum("commands" in prompt for prompt in prompts) == 2
    assert sum("restart" in prompt for prompt in prompts) == 2
    assert "Thank you for playing" in output


def test_normal_completion_restarts_with_new_configuration_and_reprompts_invalid_menu_choice(
    monkeypatch, capsys
):
    answers = iter(["3 3 H@~~", "D", "X", "S", "3 3 H@~~", "D", "Q"])
    prompts = []

    def answer(prompt):
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", answer)

    main()

    output = capsys.readouterr().out
    assert output.count("Game Over") == 2
    assert sum("height" in prompt for prompt in prompts) == 2
    assert "Invalid input. Please enter 'S' or 'Q'." in output
    assert output.count("Thank you for playing") == 1


def test_restart_uses_a_new_configuration(monkeypatch, capsys):
    answers = iter(
        [
            "3 1 H@~~",
            "D",
            "S",
            "4 1 H^**",
            "D",
            "Q",
        ]
    )
    prompts = []

    def answer(prompt):
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", answer)

    main()

    output = capsys.readouterr().out
    assert output.count("Game Over") == 2
    assert sum("height" in prompt for prompt in prompts) == 2
    assert "| ^ * * . |" in output


def test_restart_creates_a_fresh_game_from_new_configuration(monkeypatch):
    from app.game import Game

    games = []
    real_game = Game

    def track_game(**kwargs):
        game = real_game(**kwargs)
        games.append(game)
        return game

    answers = iter(["3 3 H@~~", "D", "S", "4 3 V^**", "D", "Q"])
    monkeypatch.setattr("app.main.Game", track_game)
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    main()

    assert len(games) == 2
    assert games[0] is not games[1]
    assert (games[1].height, games[1].width) == (3, 4)
    assert games[1].board == [
        [".", ".", "^", "."],
        [".", ".", "*", "."],
        [".", ".", "*", "."],
    ]
    assert games[0].board != games[1].board
