from dataclasses import dataclass, field

from .brick import Brick
from .errors import (
    InvalidCommandError,
    SpawnError,
)

EMPTY_CELL = "."
Cell = tuple[int, int, str]


@dataclass
class Game:
    height: int
    width: int

    bricks: list[Brick]
    board: list[list[str]] = field(init=False)
    active_brick: list[Cell] = field(init=False, default_factory=list)
    frame: int = 0

    def __post_init__(self):
        # Initialize the board with empty spaces
        self.board = [["." for _ in range(self.width)] for _ in range(self.height)]
        self.active_brick = []

    def spawn_brick(self, brick: Brick):
        if brick.direction == "H":
            col = (self.width - len(brick.symbols)) // 2
            candidate_cells = [
                (0, col + i, symbol) for i, symbol in enumerate(brick.symbols)
            ]
        else:  # Vertical brick
            col = self.width // 2
            candidate_cells = [
                (i, col, symbol) for i, symbol in enumerate(brick.symbols)
            ]
        if not self._can_place(candidate_cells):
            raise SpawnError(
                f"Cannot spawn brick {brick.direction}{''.join(brick.symbols)}: "
                "it does not fit or its starting cells are occupied."
            )
        self.active_brick = candidate_cells

    def lock_brick(self):
        for row, col, symbol in self.active_brick:
            self.board[row][col] = symbol
        self.active_brick = []
        self.clear_matches()

    def _can_place(self, cells: list[Cell]) -> bool:
        return all(
            0 <= row < self.height
            and 0 <= col < self.width
            and self.board[row][col] == EMPTY_CELL
            for row, col, _ in cells
        )

    def _move_cells(self, row_change: int, col_change: int):
        return [
            (row + row_change, col + col_change, symbol)
            for row, col, symbol in self.active_brick
        ]

    def _try_move(self, row_change: int, col_change: int):
        if not self.active_brick:
            return False

        new_positions = self._move_cells(row_change, col_change)
        if not self._can_place(new_positions):
            return False
        self.active_brick = new_positions
        return True

    def move_brick(self, command: str):
        if command not in ("L", "R", "D"):
            raise InvalidCommandError(f"Invalid command {command}. Use L, R, or D.")

        if command == "D":
            while self._try_move(1, 0):
                pass
            return

        moves = {"L": (0, -1), "R": (0, 1)}
        row_change, col_change = moves[command]
        self._try_move(row_change, col_change)

    def find_matches(self):
        matches = set()

        # Check horizontal similar shapes
        for row in range(self.height):
            col = 0

            while col < self.width:
                symbol = self.board[row][col]
                end_col = col + 1

                while end_col < self.width and self.board[row][end_col] == symbol:
                    end_col += 1

                if symbol != EMPTY_CELL and end_col - col >= 3:
                    for match_col in range(col, end_col):
                        matches.add((row, match_col))

                col = end_col

        # Check vertical similar shapes
        for col in range(self.width):
            row = 0

            while row < self.height:
                symbol = self.board[row][col]
                end_row = row + 1

                while end_row < self.height and self.board[end_row][col] == symbol:
                    end_row += 1

                if symbol != EMPTY_CELL and end_row - row >= 3:
                    for match_row in range(row, end_row):
                        matches.add((match_row, col))

                row = end_row

        return matches

    def clear_matches(self):
        matches = self.find_matches()

        for row, col in matches:
            self.board[row][col] = EMPTY_CELL

    def print_board(self):
        print("Frame:", self.frame)
        display_board = [row.copy() for row in self.board]
        for row, col, symbol in self.active_brick:
            display_board[row][col] = symbol

        for row in display_board:
            print("|", " ".join(row), "|")

    def start(self):
        for brick in self.bricks:
            self.spawn_brick(brick)
            self.frame += 1

            while self.active_brick:
                try:
                    self.print_board()
                    command = (
                        input(
                            "Enter up to 2 commands to process before moving to the next frame (valid commands are L, R, D): "
                        )
                        .strip()
                        .upper()
                    )

                    # Only looks at the first two commands, ignoring any additional input
                    for cmd in command[:2]:
                        self.move_brick(cmd)

                    if self._try_move(1, 0):
                        self.frame += 1
                    else:
                        self.lock_brick()
                        break
                except InvalidCommandError as e:
                    print(e)
                    continue

        self.frame += 1
        self.print_board()
        print("Game Over")
