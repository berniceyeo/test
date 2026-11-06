class BrickError(ValueError):
    """Base error for all invalid bricks."""


class BrickStructureError(BrickError):
    """Brick is missing its direction or symbols."""


class InvalidBrickDirectionError(BrickError):
    """Brick direction is not H or V."""


class InvalidBrickSymbolError(BrickError):
    """Brick contains an unsupported symbol."""


class GameError(ValueError):
    """Base error for all game-related issues."""


class InvalidInputError(GameError):
    """Invalid input provided for game configuration."""


class SpawnError(GameError):
    """A brick cannot be spawned because it is blocked or does not fit."""


class InvalidCommandError(GameError):
    """Invalid command provided for moving the brick."""
