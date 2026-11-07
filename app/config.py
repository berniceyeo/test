"""Configuration for a new Match-3 game."""

from dataclasses import dataclass

from .brick import Brick


@dataclass(frozen=True, kw_only=True)
class GameConfig:
    """Parsed dimensions and an immutable sequence of bricks."""

    width: int
    height: int
    bricks: tuple[Brick, ...]
