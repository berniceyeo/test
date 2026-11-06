import pytest

from app.brick import Brick
from app.errors import InvalidCommandError, SpawnError
from app.game import Game


@pytest.mark.parametrize(
    ("height", "width", "brick_text", "expected_cells"),
    [
        (4, 5, "H@~~", [(0, 1, "@"), (0, 2, "~"), (0, 3, "~")]),
        (4, 4, "H@~~", [(0, 0, "@"), (0, 1, "~"), (0, 2, "~")]),
        (5, 5, "V@~~", [(0, 2, "@"), (1, 2, "~"), (2, 2, "~")]),
        (5, 4, "V@~~", [(0, 2, "@"), (1, 2, "~"), (2, 2, "~")]),
    ],
)
def test_brick_spawns_at_top_center(
    height: int,
    width: int,
    brick_text: str,
    expected_cells: list[tuple[int, int, str]],
) -> None:
    game = Game(height=height, width=width, bricks=[])

    game.spawn_brick(Brick.from_text(brick_text))

    assert game.active_brick == expected_cells


@pytest.mark.parametrize(
    ("command", "expected_cells"),
    [
        ("L", [(0, 0, "@"), (0, 1, "~"), (0, 2, "~")]),
        ("R", [(0, 2, "@"), (0, 3, "~"), (0, 4, "~")]),
        ("D", [(3, 1, "@"), (3, 2, "~"), (3, 3, "~")]),
    ],
)
def test_move_brick(command: str, expected_cells: list[tuple[int, int, str]]) -> None:
    game = Game(height=4, width=5, bricks=[])
    game.spawn_brick(Brick.from_text("H@~~"))

    game.move_brick(command)

    assert game.active_brick == expected_cells


def test_rejects_invalid_command() -> None:
    game = Game(height=4, width=5, bricks=[])

    with pytest.raises(InvalidCommandError):
        game.move_brick("X")


def test_locked_board_cell_blocks_sideways_move() -> None:
    game = Game(height=4, width=5, bricks=[])
    game.board[0][0] = "#"
    game.spawn_brick(Brick.from_text("H@~~"))

    game.move_brick("L")

    assert game.active_brick == [(0, 1, "@"), (0, 2, "~"), (0, 3, "~")]


def test_failed_spawn_leaves_no_active_brick() -> None:
    game = Game(height=4, width=3, bricks=[])
    game.board[0][1] = "#"

    with pytest.raises(SpawnError):
        game.spawn_brick(Brick.from_text("H@~~"))

    assert game.active_brick == []


def test_clear_matches_removes_horizontal_run_of_three() -> None:
    game = Game(height=4, width=4, bricks=[])
    game.board[2] = ["@", "@", "@", "."]

    game.clear_matches()

    assert game.board[2] == [".", ".", ".", "."]


def test_clear_matches_removes_vertical_run_of_three() -> None:
    game = Game(height=4, width=4, bricks=[])
    game.board[0][1] = "~"
    game.board[1][1] = "~"
    game.board[2][1] = "~"

    game.clear_matches()

    assert game.board[0][1] == "."
    assert game.board[1][1] == "."
    assert game.board[2][1] == "."


def test_clear_matches_keeps_different_symbols() -> None:
    game = Game(height=4, width=4, bricks=[])
    game.board[2] = ["@", "@", "~", "."]

    game.clear_matches()

    assert game.board[2] == ["@", "@", "~", "."]


def test_matching_brick_clears_only_after_locking() -> None:
    game = Game(height=4, width=3, bricks=[])
    game.spawn_brick(Brick.from_text("H@@@"))

    game.move_brick("D")

    # Dropping keeps the matching brick active.
    assert game.active_brick == [
        (3, 0, "@"),
        (3, 1, "@"),
        (3, 2, "@"),
    ]
    assert game.board == [["."] * 3 for _ in range(4)]

    game.lock_brick()

    # Locking writes the symbols and clears their match.
    assert game.active_brick == []
    assert game.board == [["."] * 3 for _ in range(4)]


def test_locking_new_brick_clears_match_with_earlier_bricks() -> None:
    game = Game(height=4, width=3, bricks=[])

    # Two earlier bricks leave two vertically adjacent @ symbols.
    for text in ("H@~~", "H@#*"):
        game.spawn_brick(Brick.from_text(text))
        game.move_brick("D")
        game.lock_brick()

    game.spawn_brick(Brick.from_text("H@*#"))
    game.move_brick("D")

    # The third @ does not count until the new brick is locked.
    assert game.active_brick == [(1, 0, "@"), (1, 1, "*"), (1, 2, "#")]
    assert game.board == [
        [".", ".", "."],
        [".", ".", "."],
        ["@", "#", "*"],
        ["@", "~", "~"],
    ]

    game.lock_brick()

    # All three @ symbols clear; the other symbols from every brick remain.
    assert game.active_brick == []
    assert game.board == [
        [".", ".", "."],
        [".", "*", "#"],
        [".", "#", "*"],
        [".", "~", "~"],
    ]


def test_start_drops_and_locks_two_bricks(monkeypatch) -> None:
    game = Game(
        height=4,
        width=3,
        bricks=[
            Brick.from_text("H@~~"),
            Brick.from_text("H#**"),
        ],
    )

    commands = iter(["D", "D"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(commands))

    game.start()

    assert game.active_brick == []
    assert game.board == [
        [".", ".", "."],
        [".", ".", "."],
        ["#", "*", "*"],
        ["@", "~", "~"],
    ]
