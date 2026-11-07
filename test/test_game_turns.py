import pytest

from app.brick import Brick
from app.game import Game
from app.models import Cell, Command


def test_turns_apply_gravity_and_progress_through_all_bricks():
    game = Game(height=3, width=3, bricks=[
        Brick.from_text("H@~~"), Brick.from_text("H^**")
    ])
    game.start()
    assert game.frame == 1
    assert not game.is_over

    game.step([])
    assert game.frame == 2
    assert game.active_brick == [Cell(1, 0, "@"), Cell(1, 1, "~"), Cell(1, 2, "~")]

    game.step([Command.DROP])
    assert game.frame == 3
    assert game.board[2] == list("@~~")
    assert game.active_brick == [Cell(0, 0, "^"), Cell(0, 1, "*"), Cell(0, 2, "*")]
    assert not game.is_over

    game.step([Command.DROP])
    assert game.is_over
    assert game.frame == 4
    assert game.active_brick == []
    assert game.board == [list("..."), list("^**"), list("@~~")]


@pytest.mark.parametrize("third_command", [Command.LEFT, Command.DROP])
def test_step_ignores_third_command_and_applies_gravity(third_command):
    game = Game(height=4, width=9, bricks=[Brick.from_text("H@~~")])
    game.start()

    game.step([Command.LEFT, Command.LEFT, third_command])

    assert game.active_brick == [Cell(1, 1, "@"), Cell(1, 2, "~"), Cell(1, 3, "~")]
    assert game.frame == 2
    assert not game.is_over
    assert game.board == [list(".........") for _ in range(4)]


def test_lock_clears_matches_before_spawning_next_brick():
    game = Game(height=1, width=3, bricks=[
        Brick.from_text("H@@@"), Brick.from_text("H^**")
    ])
    game.start()
    game.step([])
    assert not game.is_over
    assert game.board == [list("...")]
    assert game.active_brick == [Cell(0, 0, "^"), Cell(0, 1, "*"), Cell(0, 2, "*")]


def test_blocked_next_brick_ends_game_after_advancing_frame():
    game = Game(height=1, width=3, bricks=[
        Brick.from_text("H@~~"), Brick.from_text("H^**")
    ])
    game.start()
    game.step([])
    assert game.is_over
    assert game.frame == 2
    assert game.active_brick == []
    assert game.board == [list("@~~")]


def test_oversized_first_brick_ends_game_on_start():
    game = Game(height=1, width=2, bricks=[Brick.from_text("H@~~")])
    game.start()
    assert game.is_over
    assert game.frame == 1
    assert game.active_brick == []
    assert game.board == [list("..")]


def test_empty_game_completes_on_start():
    game = Game(height=1, width=3, bricks=[])
    game.start()
    assert game.is_over
    assert game.frame == 1


def test_games_consume_bricks_independently_without_changing_configuration():
    bricks = [Brick.from_text("H@~~"), Brick.from_text("H^**")]
    original = tuple(bricks)
    first = Game(height=2, width=3, bricks=bricks)
    second = Game(height=2, width=3, bricks=bricks)

    first.start()
    first.step([Command.DROP])
    first.step([Command.DROP])
    second.start()

    assert first.is_over
    assert first.display_board() == [list("^**"), list("@~~")]
    assert not second.is_over
    assert second.display_board() == [list("@~~"), list("...")]
    assert tuple(bricks) == original
