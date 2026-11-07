import pytest

from app.controller import parse_commands
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


@pytest.mark.parametrize("command_text", ["X", "XY", "", " \t "])
def test_parse_commands_returns_no_commands_when_input_has_no_valid_commands(
    command_text,
) -> None:
    assert parse_commands(command_text) == []
