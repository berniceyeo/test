"""Domain values used by the Match-3 game."""

from enum import Enum


class Command(str, Enum):
    """Commands accepted while a brick is falling."""

    LEFT = "L"
    RIGHT = "R"
    DROP = "D"


class Direction(str, Enum):
    """Orientations supported by a brick."""

    HORIZONTAL = "H"
    VERTICAL = "V"
