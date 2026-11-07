import pytest

from app.errors import ExceedMaxBoardSize, InvalidInputError
from app.main import main, parse_to_valid_inputs
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
    width, height, bricks = parse_to_valid_inputs(" 4  5 H@~~ V^** ")
    assert (width, height) == (4, 5)
    assert [(brick.direction, brick.symbols) for brick in bricks] == [
        (Direction.HORIZONTAL, ["@", "~", "~"]),
        (Direction.VERTICAL, ["^", "*", "*"]),
    ]


def test_rejects_configuration_with_more_than_five_bricks():
    with pytest.raises(InvalidInputError):
        parse_to_valid_inputs("4 3 H@~~ H@~~ H@~~ H@~~ H@~~ H@~~")


@pytest.mark.parametrize("config", ["101 100 H@~~", "100 101 H@~~"])
def test_rejects_configuration_larger_than_maximum_board(config):
    with pytest.raises(ExceedMaxBoardSize):
        parse_to_valid_inputs(config)


def test_accepts_maximum_board_size():
    width, height, _ = parse_to_valid_inputs("100 100 H@~~")
    assert (width, height) == (100, 100)


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
