import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_terminal_game_runs_with_piped_stdin() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "app.main"],
        cwd=PROJECT_ROOT,
        input="3 1 H@~~\nD\nQ\n",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Welcome to Match-3 game!" in result.stdout
    assert "Game Over" in result.stdout
    assert "Thank you for playing Match-3!" in result.stdout
    assert result.stderr == ""
