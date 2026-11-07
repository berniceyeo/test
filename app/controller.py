"""Terminal controller for running a Match-3 game."""

from .brick import Brick
from .config import GameConfig
from .constants import MAX_BRICKS, MAX_COMMANDS_PER_TURN, MAX_HEIGHT, MAX_WIDTH
from .errors import ExceedMaxBoardSizeError, InvalidInputError
from .game import Game
from .models import Command
from .user_input import read_input


def prompt_for_configuration() -> GameConfig:
    """Prompt until a valid terminal game configuration is supplied."""
    while True:
        try:
            config_text = read_input(
                f"Please enter field size (width, height) and up to {MAX_BRICKS} bricks: "
            )
            return parse_to_valid_inputs(config_text)
        except ValueError as error:
            print(error)


def parse_to_valid_inputs(config_text: str) -> GameConfig:
    """Parse and validate game configuration. Check if the inputs are valid inputs."""
    inputs = config_text.split()

    if len(inputs) < 3:
        raise InvalidInputError("Example: 5 3 H@~~")

    width_text, height_text, brick_texts = inputs[0], inputs[1], inputs[2:]

    try:
        width = int(width_text)
        height = int(height_text)

    except ValueError as error:
        raise InvalidInputError("Width and height must be whole numbers.") from error

    if height <= 0 or width <= 0:
        raise InvalidInputError("Height and width must be greater than zero.")

    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise ExceedMaxBoardSizeError(
            f"Board cannot exceed {MAX_WIDTH} columns by {MAX_HEIGHT} rows."
        )

    if len(brick_texts) > MAX_BRICKS:
        raise InvalidInputError(f"Enter no more than {MAX_BRICKS} bricks.")

    bricks = tuple(Brick.from_text(text) for text in brick_texts)
    return GameConfig(width=width, height=height, bricks=bricks)


def run_game(game: Game) -> None:
    """Run all configured bricks through the terminal interface."""
    game.start()
    while not game.is_over:
        print_board(game)
        command_text = read_input(
            f"Enter up to {MAX_COMMANDS_PER_TURN} commands to process before moving to the next frame "
            "(valid commands are L, R, D): "
        )
        commands = parse_commands(command_text)
        if command_text.strip() and not commands:
            print("Invalid input. No valid commands found; use L, R, or D.")
        game.step(commands)

    print_board(game)
    print("Game Over.")


def parse_commands(command_text: str) -> list[Command]:
    """Return the first two valid commands, ignoring whitespace and other text."""
    commands = []

    for character in "".join(command_text.split()).upper():
        try:
            commands.append(Command(character))
        except ValueError:
            continue

        if len(commands) == MAX_COMMANDS_PER_TURN:
            break

    return commands


def print_board(game: Game) -> None:
    """Render the current game state in the terminal."""
    print("Frame ", game.frame)
    for row in game.display_board():
        print("|", " ".join(row), "|")
