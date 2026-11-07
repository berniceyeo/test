import subprocess
import sys
from pathlib import Path

import pytest

from app.constants import MAX_BRICKS

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_terminal_game(input_text: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "app.main"],
        cwd=PROJECT_ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )


def assert_clean_exit(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0
    assert result.stderr == ""


def test_terminal_game_runs_with_piped_stdin() -> None:
    result = run_terminal_game("3 1 H@~~\nD\nQ\n")

    assert_clean_exit(result)
    assert "Welcome to Match-3 game!" in result.stdout
    assert "Game Over" in result.stdout
    assert "Thank you for playing Match-3!" in result.stdout


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ("abc 1 H@~~", "Width and height must be whole numbers."),
        ("3 abc H@~~", "Width and height must be whole numbers."),
        (
            "3 1 " + " ".join(["H@~~"] * (MAX_BRICKS + 1)),
            f"Enter no more than {MAX_BRICKS} bricks.",
        ),
    ],
    ids=["non-numeric-width", "non-numeric-height", "too-many-bricks"],
)
def test_terminal_game_recovers_from_invalid_configuration(config, message) -> None:
    result = run_terminal_game(f"{config}\n3 1 H@~~\nD\nQ\n")

    assert_clean_exit(result)
    assert message in result.stdout
    assert result.stdout.count("Please enter field size") == 2
    assert result.stdout.count("Game Over") == 1
    assert "| @ ~ ~ |" in result.stdout
    assert "Input closed" not in result.stdout
    assert "Thank you for playing Match-3!" in result.stdout


@pytest.mark.parametrize(
    ("command_text", "error_count"),
    [("XY", 1), ("", 0), (" \t ", 0)],
    ids=["invalid", "blank", "whitespace"],
)
def test_terminal_game_advances_without_valid_commands(command_text, error_count) -> None:
    result = run_terminal_game(f"3 2 H@~~\n{command_text}\nD\nQ\n")

    assert_clean_exit(result)
    assert "Frame: 1\n| @ ~ ~ |\n| . . . |" in result.stdout
    # The next movement prompt must follow the board after gravity, before D.
    assert (
        "Frame: 2\n| . . . |\n| @ ~ ~ |\nEnter up to 2 commands"
        in result.stdout
    )
    assert result.stdout.count("Enter up to 2 commands") == 2
    assert result.stdout.count("Game Over") == 1
    assert result.stdout.count("Enter 'S' to restart") == 1
    assert result.stdout.count(
        "Invalid input. No valid commands found; use L, R, or D."
    ) == error_count
    assert "Invalid input. Please enter 'S' or 'Q'." not in result.stdout
    assert "Input closed" not in result.stdout
    assert "Thank you for playing Match-3!" in result.stdout


@pytest.mark.parametrize(
    ("initial_input", "command_prompts", "final_board"),
    [
        ("2 1 H@~~\n", 0, "Frame: 0\n| . . |"),
        ("3 1 H@~~ H^**\nD\n", 1, "Frame: 1\n| @ ~ ~ |"),
    ],
    ids=["brick-does-not-fit", "spawn-cells-occupied"],
)
def test_terminal_game_handles_spawn_failure(
    initial_input, command_prompts, final_board
) -> None:
    result = run_terminal_game(initial_input + "Q\n")

    assert_clean_exit(result)
    assert result.stdout.count("Game Over") == 1
    assert f"{final_board}\nGame Over\n" in result.stdout
    assert result.stdout.count("Enter up to 2 commands") == command_prompts
    assert result.stdout.count("Enter 'S' to restart") == 1
    assert "Input closed" not in result.stdout
    assert "Thank you for playing Match-3!" in result.stdout


@pytest.mark.parametrize(
    ("input_text", "last_prompt"),
    [
        ("", "Please enter field size"),
        ("3 1 H@~~\n", "Enter up to 2 commands"),
        ("3 1 H@~~\nD\n", "Enter 'S' to restart"),
        ("3 1 H@~~\nD\nS\n", "Please enter field size"),
    ],
    ids=["setup", "movement", "restart-menu", "setup-after-restart"],
)
def test_terminal_game_exits_cleanly_when_stdin_is_closed(input_text, last_prompt) -> None:
    result = run_terminal_game(input_text)

    assert_clean_exit(result)
    assert "Input closed. Thank you for playing Match-3!" in result.stdout
    assert last_prompt in result.stdout
    assert result.stdout.count("Input closed.") == 1
