from .brick import Brick
from .constants import MAX_BRICKS, MAX_HEIGHT, MAX_WIDTH
from .errors import (
    ExceedMaxBoardSize,
    InvalidInputError,
    SpawnError,
)
from .game import Game
from .user_input import read_input


def parse_to_valid_inputs(config_text: str):
    inputs = config_text.split()

    if len(inputs) < 3:
        raise InvalidInputError("Example: 5 3 H@~~")

    width_text, height_text, brick_texts = inputs[0], inputs[1], inputs[2:]
    width = int(width_text)
    height = int(height_text)

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


def main():
    print("Welcome to Match-3 game!")

    while True:
        while True:
            try:
                inputs = read_input(
                    "Please enter field size (width, height) and up to 5 bricks: "
                )
                width, height, bricks = parse_to_valid_inputs(inputs)
                break

            except ValueError as error:
                print(error)
                continue

        try:
            game = Game(height=height, width=width, bricks=bricks)
            game.start()

        except SpawnError:
            print("Game Over")

        while True:
            choice = read_input("Enter 'S' to restart or 'Q' to quit: ").strip().upper()

            if choice == "Q":
                print("Thank you for playing Match-3!")
                return

            if choice == "S":
                break

            print("Invalid input. Please enter 'S' or 'Q'.")


if __name__ == "__main__":
    main()
