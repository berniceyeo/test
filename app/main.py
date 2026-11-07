from .controller import prompt_for_configuration, run_game
from .errors import SpawnError
from .game import Game
from .user_input import read_input


def main():
    print("Welcome to Match-3 game!")

    while True:
        width, height, bricks = prompt_for_configuration()

        try:
            game = Game(height=height, width=width, bricks=bricks)
            run_game(game)

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
