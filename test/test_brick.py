import re

import pytest

from app.brick import Brick
from app.errors import (
    BrickStructureError,
    InvalidBrickDirectionError,
    InvalidBrickSymbolError,
)
from app.models import Direction


def test_rejects_invalid_direction() -> None:
    with pytest.raises(
        InvalidBrickDirectionError,
        match=re.escape("Invalid brick X: direction must be H or V"),
    ):
        Brick.from_text("X@~*")


@pytest.mark.parametrize(
    ("direction", "symbols"),
    [
        (Direction.HORIZONTAL, ["@", "~"]),
        (Direction.VERTICAL, ["@", "~", "@", "@"]),
    ],
)
def test_rejects_brick_with_length_other_than_three(
    direction: Direction, symbols: list[str]
) -> None:
    with pytest.raises(BrickStructureError, match=re.escape("Brick must have three symbols")):
        Brick(direction=direction, symbols=symbols)


def test_rejects_invalid_symbol() -> None:
    with pytest.raises(InvalidBrickSymbolError, match=re.escape("Invalid symbol(s) ['X']")):
        Brick(direction=Direction.VERTICAL, symbols=["@", "~", "X"])


@pytest.mark.parametrize(
    ("text", "direction"),
    [("H@~~", Direction.HORIZONTAL), ("V@~~", Direction.VERTICAL)],
)
def test_creates_valid_brick_from_text(text: str, direction: Direction) -> None:
    brick = Brick.from_text(text)

    assert brick.direction is direction
    assert brick.symbols == ["@", "~", "~"]


def test_empty_brick_text_is_rejected() -> None:
    with pytest.raises(BrickStructureError, match=re.escape("Please enter valid Brick")):
        Brick.from_text("")
