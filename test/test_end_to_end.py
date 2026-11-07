import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_terminal_game(input_text: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "app.main"],
        cwd=PROJECT_ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
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


def test_terminal_game_recovers_from_invalid_configuration() -> None:
    result = run_terminal_game("abc 1 H@~~\n3 1 H@~~\nD\nQ\n")

    assert_clean_exit(result)
    assert "Width and height must be whole numbers." in result.stdout
    assert "Game Over" in result.stdout


def test_terminal_game_reprompts_after_all_invalid_commands() -> None:
    result = run_terminal_game("3 1 H@~~\nXX\nD\nQ\n")

    assert_clean_exit(result)
    assert "Invalid input. Please enter at least one command: L, R, or D." in result.stdout
    assert "Game Over" in result.stdout


def test_terminal_game_handles_spawn_failure() -> None:
    result = run_terminal_game("3 1 H@~~ H^**\nD\nQ\n")

    assert_clean_exit(result)
    assert "Cannot spawn brick H^**" not in result.stdout
    assert result.stdout.count("Game Over") == 1


def test_terminal_game_exits_cleanly_when_stdin_is_closed() -> None:
    result = run_terminal_game("")

    assert_clean_exit(result)
    assert "Input closed. Thank you for playing Match-3!" in result.stdout
