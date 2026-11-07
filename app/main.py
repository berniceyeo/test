from .controller import prompt_for_configuration, run_game
from .game import Game
from .user_input import read_input


def main():
    print("Welcome to Match-3 game!")

    while True:
        config = prompt_for_configuration()

        game = Game(height=config.height, width=config.width, bricks=config.bricks)
        run_game(game)

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
