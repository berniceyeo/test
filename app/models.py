"""Domain values used by the Match-3 game."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from .brick import Brick


class Command(str, Enum):
    """Commands accepted while a brick is falling."""

    LEFT = "L"
    RIGHT = "R"
    DROP = "D"


class Direction(str, Enum):
    """Orientations supported by a brick."""

    HORIZONTAL = "H"
    VERTICAL = "V"


class Cell(NamedTuple):
    """A brick symbol at a row and column on the board."""

    row: int
    col: int
    symbol: str


@dataclass(frozen=True, kw_only=True)
class GameConfig:
    """Parsed dimensions and bricks for a new game."""

    width: int
    height: int
    bricks: list["Brick"]
