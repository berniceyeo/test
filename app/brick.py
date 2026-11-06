from dataclasses import dataclass

from .errors import (
    BrickStructureError,
    InvalidBrickDirectionError,
    InvalidBrickSymbolError,
)


@dataclass
class Brick:
    direction: str
    symbols: list[str]

    def __post_init__(self):
        if self.direction not in ("H", "V"):
            raise InvalidBrickDirectionError(
                f"Invalid brick {self.direction}: direction must be H or V"
            )

        if len(self.symbols) < 3:
            raise BrickStructureError("Brick must contain at least three symbols")

        allowed_symbols = {"@", "#", "~", "*"}
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
