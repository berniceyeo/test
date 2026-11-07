import pytest

from app.controller import parse_commands, prompt_for_commands
from app.models import Command


@pytest.mark.parametrize(
    ("command_text", "expected_commands"),
    [
        ("L X", [Command.LEFT]),
        ("XLR", [Command.LEFT, Command.RIGHT]),
        ("LRD", [Command.LEFT, Command.RIGHT]),
        ("d r", [Command.DROP, Command.RIGHT]),
    ],
)
def test_parse_commands_keeps_the_first_two_valid_commands(
    command_text, expected_commands
) -> None:
    assert parse_commands(command_text) == expected_commands


def test_prompt_for_commands_reprompts_when_no_valid_command_is_supplied(
    monkeypatch, capsys
) -> None:
    answers = iter(["XX", "L R"])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    assert prompt_for_commands() == [Command.LEFT, Command.RIGHT]
    assert "Invalid input. Please enter at least one command: L, R, or D." in capsys.readouterr().out
