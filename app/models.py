"""Domain values used by the Match-3 game."""

from enum import Enum
from typing import NamedTuple


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
