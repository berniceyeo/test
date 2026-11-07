from dataclasses import dataclass, field

from .brick import Brick
from .constants import EMPTY_CELL
from .errors import (
    InvalidCommandError,
    SpawnError,
)
from .models import Command, Direction

Cell = tuple[int, int, str]


def clear_matches(board: list[list[str]]) -> None:
    """Remove every horizontal or vertical run of at least three symbols."""
    matches = set()
    height = len(board)
    width = len(board[0]) if board else 0

    for row in range(height):
        col = 0
        while col < width:
            symbol = board[row][col]
            end_col = col + 1
            while end_col < width and board[row][end_col] == symbol:
                end_col += 1
            if symbol != EMPTY_CELL and end_col - col >= 3:
                matches.update((row, match_col) for match_col in range(col, end_col))
            col = end_col

    for col in range(width):
        row = 0
        while row < height:
            symbol = board[row][col]
            end_row = row + 1
            while end_row < height and board[end_row][col] == symbol:
                end_row += 1
            if symbol != EMPTY_CELL and end_row - row >= 3:
                matches.update((match_row, col) for match_row in range(row, end_row))
            row = end_row

    for row, col in matches:
        board[row][col] = EMPTY_CELL


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
        self.board = [
            [EMPTY_CELL for _ in range(self.width)] for _ in range(self.height)
        ]
        self.active_brick = []

    def spawn_brick(self, brick: Brick):
        if brick.direction is Direction.HORIZONTAL:
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
                f"Cannot spawn brick {brick.direction.value}{''.join(brick.symbols)}: "
                "it does not fit or its starting cells are occupied."
            )
        self.active_brick = candidate_cells

    def lock_brick(self):
        for row, col, symbol in self.active_brick:
            self.board[row][col] = symbol
        self.active_brick = []
        clear_matches(self.board)

    def begin_brick(self, brick: Brick) -> None:
        self.spawn_brick(brick)
        self.frame += 1

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

    def move_brick(self, command: Command | str):
        try:
            command = Command(command)
        except ValueError:
            raise InvalidCommandError(f"Invalid command {command}. Use L, R, or D.")

        if command is Command.DROP:
            while self._try_move(1, 0):
                pass
            return

        moves = {Command.LEFT: (0, -1), Command.RIGHT: (0, 1)}
        row_change, col_change = moves[command]
        self._try_move(row_change, col_change)

    def process_commands(self, commands: list[Command]) -> None:
        for command in commands:
            self.move_brick(command)

    def advance_frame(self) -> bool:
        """Move the active brick down one row, locking it when it cannot move."""
        if self._try_move(1, 0):
            self.frame += 1
            return True

        self.lock_brick()
        return False

    def complete(self) -> None:
        self.frame += 1

    def display_board(self) -> list[list[str]]:
        display_board = [row.copy() for row in self.board]
        for row, col, symbol in self.active_brick:
            display_board[row][col] = symbol
        return display_board
