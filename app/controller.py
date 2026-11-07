"""Terminal controller for running a Match-3 game."""

from .brick import Brick
from .constants import MAX_BRICKS, MAX_HEIGHT, MAX_WIDTH
from .errors import ExceedMaxBoardSize, InvalidInputError
from .game import Game
from .models import Command
from .user_input import read_input

COMMAND_PROMPT = (
    "Enter up to 2 commands to process before moving to the next frame "
    "(valid commands are L, R, D): "
)


def parse_to_valid_inputs(config_text: str) -> tuple[int, int, list[Brick]]:
    """Parse and validate a width-first game configuration."""
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
        raise ExceedMaxBoardSize(
            f"Board cannot exceed {MAX_WIDTH} columns by {MAX_HEIGHT} rows."
        )

    if len(brick_texts) > MAX_BRICKS:
        raise InvalidInputError(f"Enter no more than {MAX_BRICKS} bricks.")

    bricks = [Brick.from_text(text) for text in brick_texts]
    return width, height, bricks


def prompt_for_configuration() -> tuple[int, int, list[Brick]]:
    """Prompt until a valid terminal game configuration is supplied."""
    while True:
        try:
            config_text = read_input(
                f"Please enter field size (width, height) and up to {MAX_BRICKS} bricks: "
            )
            return parse_to_valid_inputs(config_text)
        except ValueError as error:
            print(error)


def parse_commands(command_text: str) -> list[Command]:
    """Return the first two valid commands, ignoring whitespace and other text."""
    commands = []

    for character in "".join(command_text.split()).upper():
        try:
            commands.append(Command(character))
        except ValueError:
            continue

        if len(commands) == 2:
            break

    return commands


def print_board(game: Game) -> None:
    """Render the current game state in the terminal."""
    print("Frame:", game.frame)
    for row in game.display_board():
        print("|", " ".join(row), "|")


def run_game(game: Game) -> None:
    """Run all configured bricks through the terminal interface."""
    for brick in game.bricks:
        if not game.begin_brick(brick):
            break

        while game.active_brick:
            print_board(game)
            commands = parse_commands(read_input(COMMAND_PROMPT))

            game.process_commands(commands)
            game.advance_frame()

    else:
        game.complete()
        print_board(game)
    print("Game Over")
