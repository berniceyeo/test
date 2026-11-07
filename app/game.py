from collections.abc import Sequence

from .brick import Brick
from .constants import EMPTY_CELL, MAX_COMMANDS_PER_TURN
from .models import Cell, Command, Direction


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


class Game:
    def __init__(
        self, height: int, width: int, bricks: Sequence[Brick], frame: int = 0
    ) -> None:
        self.height = height
        self.width = width
        self.frame = frame
        self.is_over = False
        self.board = [
            [EMPTY_CELL for _ in range(self.width)] for _ in range(self.height)
        ]
        self.active_brick: list[Cell] = []
        self.bricks = list(bricks)

    def start(self) -> None:
        """Start this game once, spawning its first configured brick."""
        self._spawn_next_brick()

    def _spawn_next_brick(self) -> None:
        if not self.bricks:
            self.frame += 1
            self.is_over = True
            return

        brick = self.bricks.pop(0)
        if not self.begin_brick(brick):
            self.is_over = True
            return

    def step(self, commands: Sequence[Command]) -> None:
        """Apply a turn, gravity, locking, and progression to the next brick."""
        for command in commands[:MAX_COMMANDS_PER_TURN]:
            self.move_brick(command)

        if self._try_move(1, 0):
            self.frame += 1
        else:
            self.lock_brick()
            self._spawn_next_brick()

    def spawn_brick(self, brick: Brick) -> bool:
        """Place a brick, returning False without changing state if blocked."""
        if brick.direction is Direction.HORIZONTAL:
            col = (self.width - len(brick.symbols)) // 2
            candidate_cells = [
                Cell(0, col + i, symbol) for i, symbol in enumerate(brick.symbols)
            ]
        else:  # Vertical brick
            col = self.width // 2
            candidate_cells = [
                Cell(i, col, symbol) for i, symbol in enumerate(brick.symbols)
            ]
        if not self._can_place(candidate_cells):
            return False
        self.active_brick = candidate_cells
        return True

    def lock_brick(self):
        for cell in self.active_brick:
            self.board[cell.row][cell.col] = cell.symbol
        self.active_brick = []
        clear_matches(self.board)

    def begin_brick(self, brick: Brick) -> bool:
        if not self.spawn_brick(brick):
            return False
        self.frame += 1
        return True

    def _can_place(self, cells: list[Cell]) -> bool:
        return all(
            0 <= cell.row < self.height
            and 0 <= cell.col < self.width
            and self.board[cell.row][cell.col] == EMPTY_CELL
            for cell in cells
        )

    def _move_cells(self, row_change: int, col_change: int) -> list[Cell]:
        return [
            Cell(cell.row + row_change, cell.col + col_change, cell.symbol)
            for cell in self.active_brick
        ]

    def _try_move(self, row_change: int, col_change: int):
        if not self.active_brick:
            return False

        new_positions = self._move_cells(row_change, col_change)
        if not self._can_place(new_positions):
            return False
        self.active_brick = new_positions
        return True

    def move_brick(self, command: Command) -> None:
        """Apply a command already validated by the input boundary."""
        if command is Command.DROP:
            while self._try_move(1, 0):
                pass
            return

        moves = {Command.LEFT: (0, -1), Command.RIGHT: (0, 1)}
        row_change, col_change = moves[command]
        self._try_move(row_change, col_change)

    def display_board(self) -> list[list[str]]:
        display_board = [row.copy() for row in self.board]
        for cell in self.active_brick:
            display_board[cell.row][cell.col] = cell.symbol
        return display_board
