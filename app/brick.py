from dataclasses import dataclass

from .errors import (
    BrickStructureError,
    InvalidBrickDirectionError,
    InvalidBrickSymbolError,
)
from .models import Direction


@dataclass
class Brick:
    direction: Direction | str
    symbols: list[str]

    def __post_init__(self):
        try:
            self.direction = Direction(self.direction)
        except ValueError:
            raise InvalidBrickDirectionError(
                f"Invalid brick {self.direction}: direction must be H or V"
            )

        if len(self.symbols) != 3:
            raise BrickStructureError("Brick must have three symbols")

        allowed_symbols = {"@", "^", "~", "*"}
        invalid_symbols = set(self.symbols) - allowed_symbols

        if invalid_symbols:
            raise InvalidBrickSymbolError(
                f"Invalid symbol(s) {sorted(invalid_symbols)}"
            )

    @classmethod
    def from_text(cls, text: str):
        if not text:
            raise BrickStructureError("Please enter valid Brick")

        return cls(direction=text[0], symbols=list(text[1:]))
