from .brick import Brick
from .errors import (
    InvalidInputError,
    SpawnError,
)
from .game import Game


def parse_to_valid_inputs(config_text: str):
    inputs = config_text.split()

    if len(inputs) < 3:
        raise InvalidInputError("Example: 5 3 H@~~")

    height_text, width_text, brick_texts = inputs[0], inputs[1], inputs[2:]
    height = int(height_text)
    width = int(width_text)

    if height <= 0 or width <= 0:
        raise InvalidInputError("Height and width must be greater than zero.")

    bricks = [Brick.from_text(text) for text in brick_texts]
    return height, width, bricks


def main():
    game_initialised = False
    while not game_initialised:
        try:
            inputs = input("Enter height, width, and number of bricks: ")
            valid_inputs = parse_to_valid_inputs(inputs)
            game_initialised = True
        except ValueError as error:
            print(error)
            continue

    while True:
        height, width, bricks = valid_inputs
        game = Game(height=height, width=width, bricks=bricks)

        try:
            game.start()

        except SpawnError:
            print("Game Over")

        while True:
            choice = input("Enter 'S' to restart and 'Q' to quit: ").strip().upper()

            if choice == "Q":
                print("Thank you for playing Match-3!")
                return

            if choice == "S":
                break

            print("Invalid input. Please enter 'S' or 'Q'.")


if __name__ == "__main__":
    main()
