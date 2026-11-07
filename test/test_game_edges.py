import re

import pytest

from app.brick import Brick
from app.controller import run_game
from app.errors import SpawnError
from app.game import Game, clear_matches
from app.models import Command


@pytest.mark.parametrize("command", [Command.LEFT, Command.RIGHT])
def test_board_edge_blocks_movement(command):
    game = Game(height=4, width=3, bricks=[])
    game.spawn_brick(Brick.from_text("H@~~"))
    original = game.active_brick.copy()
    game.move_brick(command)
    assert game.active_brick == original


@pytest.mark.parametrize("height,width,text", [(4, 2, "H@~~"), (2, 4, "V@~~")])
def test_oversized_spawn_leaves_state_unchanged(height, width, text):
    game = Game(height=height, width=width, bricks=[])
    before = [row.copy() for row in game.board]
    with pytest.raises(
        SpawnError,
        match=re.escape(
            f"Cannot spawn brick {text}: it does not fit or its starting cells are occupied."
        ),
    ):
        game.spawn_brick(Brick.from_text(text))
    assert game.active_brick == []
    assert game.board == before


def test_vertical_brick_stops_above_locked_symbol():
    game = Game(height=6, width=3, bricks=[])
    game.spawn_brick(Brick.from_text("H^**"))
    game.move_brick(Command.DROP)
    game.lock_brick()
    game.spawn_brick(Brick.from_text("V@~~"))
    game.move_brick(Command.DROP)
    assert game.active_brick == [(2, 1, "@"), (3, 1, "~"), (4, 1, "~")]
    assert game.board[5][1] == "*"


def test_dr_moves_right_after_drop_before_locking(monkeypatch):
    game = Game(height=4, width=5, bricks=[Brick.from_text("H@~~")])
    answers = iter(["DR"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    run_game(game)
    assert game.board == [list("....."), list("....."), list("....."), list("..@~~")]
    assert game.active_brick == []


def test_invalid_characters_do_not_block_frame_advance(monkeypatch, capsys):
    game = Game(height=4, width=5, bricks=[Brick.from_text("H@~~")])
    snapshots = []
    answers = iter(["L X", "D"])

    def answer(_prompt):
        snapshots.append((game.frame, game.active_brick.copy()))
        return next(answers)

    monkeypatch.setattr("builtins.input", answer)
    run_game(game)
    assert snapshots == [
        (1, [(0, 1, "@"), (0, 2, "~"), (0, 3, "~")]),
        (2, [(1, 0, "@"), (1, 1, "~"), (1, 2, "~")]),
    ]
    assert game.board[3] == list("@~~..")
    assert "Invalid command" not in capsys.readouterr().out


@pytest.mark.parametrize(
    "rows,expected",
    [
        (["@@@@#"], ["....#"]),
        (["~#", "~.", "~.", "~."], [".#", "..", "..", ".."]),
        ([".@.", "@@@", ".@#"], ["...", "...", "..#"]),
        (["@..", ".@.", "..@"], ["@..", ".@.", "..@"]),
        (["@@.@"], ["@@.@"]),
        (["@@"], ["@@"]),
        (["...", "...", "..."], ["...", "...", "..."]),
    ],
    ids=["long-horizontal", "long-vertical", "crossing", "diagonal", "separated", "pair", "empty"],
)
def test_match_edge_cases(rows, expected):
    board = [list(row) for row in rows]
    clear_matches(board)
    assert board == [list(row) for row in expected]
