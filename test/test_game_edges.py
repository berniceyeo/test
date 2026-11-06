import pytest

from app.brick import Brick
from app.errors import SpawnError
from app.game import Game


@pytest.mark.parametrize("command", ["L", "R"])
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
    with pytest.raises(SpawnError):
        game.spawn_brick(Brick.from_text(text))
    assert game.active_brick == []
    assert game.board == before


def test_vertical_brick_stops_above_locked_symbol():
    game = Game(height=6, width=3, bricks=[])
    game.board[5][1] = "#"
    game.spawn_brick(Brick.from_text("V@~~"))
    game.move_brick("D")
    assert game.active_brick == [(2, 1, "@"), (3, 1, "~"), (4, 1, "~")]
    assert game.board[5][1] == "#"


def test_dr_moves_right_after_drop_before_locking(monkeypatch):
    game = Game(height=4, width=5, bricks=[Brick.from_text("H@~~")])
    answers = iter(["DR"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    game.start()
    assert game.board == [list("....."), list("....."), list("....."), list("..@~~")]
    assert game.active_brick == []


def test_lx_keeps_left_move_without_gravity_before_retry(monkeypatch, capsys):
    game = Game(height=4, width=5, bricks=[Brick.from_text("H@~~")])
    snapshots = []
    answers = iter(["LX", "D"])

    def answer(_prompt):
        snapshots.append((game.frame, game.active_brick.copy()))
        return next(answers)

    monkeypatch.setattr("builtins.input", answer)
    game.start()
    assert snapshots == [
        (1, [(0, 1, "@"), (0, 2, "~"), (0, 3, "~")]),
        (1, [(0, 0, "@"), (0, 1, "~"), (0, 2, "~")]),
    ]
    assert game.board[3] == list("@~~..")
    assert "Invalid command" in capsys.readouterr().out


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
    game = Game(height=len(rows), width=len(rows[0]), bricks=[])
    game.board = [list(row) for row in rows]
    game.clear_matches()
    assert game.board == [list(row) for row in expected]
