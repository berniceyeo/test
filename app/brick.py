from dataclasses import dataclass

from .constants import ALLOWED_SYMBOLS
from .errors import (
    BrickStructureError,
    InvalidBrickDirectionError,
    InvalidBrickSymbolError,
)
from .models import Direction


@dataclass
class Brick:
    direction: Direction
    symbols: list[str]

    def __post_init__(self):
        if len(self.symbols) != 3:
            raise BrickStructureError("Brick must have three symbols")

        invalid_symbols = set(self.symbols) - ALLOWED_SYMBOLS

        if invalid_symbols:
            raise InvalidBrickSymbolError(
                f"Invalid symbol(s) {sorted(invalid_symbols)}"
            )

    @classmethod
    def from_text(cls, text: str) -> "Brick":
        if not text:
            raise BrickStructureError("Please enter valid Brick")

        try:
            direction = Direction(text[0])
        except ValueError as error:
            raise InvalidBrickDirectionError(
                f"Invalid brick {text[0]}: direction must be "
                f"{Direction.HORIZONTAL.value} or {Direction.VERTICAL.value}"
            ) from error

        return cls(direction=direction, symbols=list(text[1:]))
