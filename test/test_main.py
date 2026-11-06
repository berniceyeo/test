import pytest

from app.main import main, parse_to_valid_inputs


@pytest.mark.parametrize("config", ["", "4 5", "abc 5 H@~~", "4 abc H@~~", "0 5 H@~~", "4 -1 H@~~", "4 5 X@~~"])
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
    height, width, bricks = parse_to_valid_inputs(" 4  5 H@~~ V#** ")
    assert (height, width) == (4, 5)
    assert [(brick.direction, brick.symbols) for brick in bricks] == [
        ("H", ["@", "~", "~"]), ("V", ["#", "*", "*"])
    ]


def test_spawn_failure_offers_restart_and_quit(monkeypatch, capsys):
    # The second brick cannot spawn on a one-row board.
    answers = iter(["1 3 H@~~ H#**", "D", "S", "D", "Q"])
    prompts = []

    def answer(prompt):
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", answer)
    main()

    output = capsys.readouterr().out
    assert output.count("Game Over") == 2
    assert sum("height" in prompt for prompt in prompts) == 1
    assert sum("commands" in prompt for prompt in prompts) == 2
    assert sum("restart" in prompt for prompt in prompts) == 2
    assert "Thank you for playing" in output


def test_normal_completion_restarts_and_reprompts_invalid_menu_choice(monkeypatch, capsys):
    answers = iter(["1 3 H@~~", "D", "X", "S", "D", "Q"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    main()

    output = capsys.readouterr().out
    assert output.count("Game Over") == 2
    assert "Invalid input. Please enter 'S' or 'Q'." in output
    assert output.count("Thank you for playing") == 1
