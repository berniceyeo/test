"""Safe terminal input for the Match-3 application."""


def read_input(prompt: str) -> str:
    """Read input or exit cleanly when the input stream has been closed or when user keyboard interrupts."""
    try:
        return input(prompt)
    except EOFError:
        print("\nInput closed. Thank you for playing Match-3!")
        raise SystemExit
    except KeyboardInterrupt:
        print("\nGame interrupted. Thank you for playing Match-3!")
        raise SystemExit
