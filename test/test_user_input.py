import pytest

from app.user_input import read_input


def test_closed_input_exits_cleanly(monkeypatch, capsys) -> None:
    def closed_input(_prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", closed_input)

    with pytest.raises(SystemExit):
        read_input("Enter a value: ")

    assert "Input closed. Thank you for playing Match-3!" in capsys.readouterr().out


def test_interrupted_input_exits_cleanly(monkeypatch, capsys) -> None:
    def interrupted_input(_prompt: str) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupted_input)

    with pytest.raises(SystemExit):
        read_input("Enter a value: ")

    assert "Game interrupted. Thank you for playing Match-3!" in capsys.readouterr().out
