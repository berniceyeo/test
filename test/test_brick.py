import pytest

from app.brick import Brick
from app.errors import (
    BrickStructureError,
    InvalidBrickDirectionError,
    InvalidBrickSymbolError,
)
from app.models import Direction


def test_rejects_invalid_direction() -> None:
    with pytest.raises(InvalidBrickDirectionError):
        Brick(direction="X", symbols=["@", "~", "*"])


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
    with pytest.raises(BrickStructureError):
        Brick(direction=direction, symbols=symbols)


def test_rejects_invalid_symbol() -> None:
    with pytest.raises(InvalidBrickSymbolError):
        Brick(direction=Direction.VERTICAL, symbols=["@", "~", "X"])


def test_creates_valid_brick_from_text() -> None:
    brick = Brick.from_text("H@~~")

    assert brick.direction is Direction.HORIZONTAL
    assert brick.symbols == ["@", "~", "~"]


def test_empty_brick_text_is_rejected() -> None:
    with pytest.raises(BrickStructureError):
        Brick.from_text("")
