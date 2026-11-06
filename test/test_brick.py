import pytest

from app.brick import Brick
from app.errors import (
    BrickStructureError,
    InvalidBrickDirectionError,
    InvalidBrickSymbolError,
)


def test_rejects_invalid_direction() -> None:
    with pytest.raises(InvalidBrickDirectionError):
        Brick(direction="X", symbols=["@", "~", "*"])


def test_rejects_brick_with_fewer_than_three_symbols() -> None:
    with pytest.raises(BrickStructureError):
        Brick(direction="H", symbols=["@", "~"])


def test_rejects_invalid_symbol() -> None:
    with pytest.raises(InvalidBrickSymbolError):
        Brick(direction="V", symbols=["@", "~", "X"])


def test_creates_valid_brick_from_text() -> None:
    brick = Brick.from_text("H@~~")

    assert brick.direction == "H"
    assert brick.symbols == ["@", "~", "~"]


def test_empty_brick_text_is_rejected() -> None:
    with pytest.raises(BrickStructureError):
        Brick.from_text("")
