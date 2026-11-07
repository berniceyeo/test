# Match-3 Brick Game

A Python terminal game where you guide horizontal or vertical bricks onto a board. Runs of three or more identical symbols clear when a brick locks.

Choose the board size and a sequence of bricks before playing. The game ends when all bricks have been placed or the next brick cannot spawn.

## Quick start

Use Python 3.10 or newer. The game itself uses only the Python standard library.

From the project root:

```sh
python -m app.main
```

At the setup prompt, enter:

```text
7 5 H@~~ V^**
```

This creates a board **7 columns wide and 5 rows high**, with a horizontal `@~~` brick followed by a vertical `^**` brick.

For a minimal game, enter these lines at the successive prompts:

```text
3 1 H@~~
D
Q
```

The brick fills the single row, the game ends, and `Q` quits.

## Configuration

```text
<width> <height> <brick> [<brick> ...]
```

| Setting          | Accepted values                                      |
| ---------------- | ---------------------------------------------------- |
| Width and height | Whole numbers from 1 to 100                          |
| Number of bricks | 1 to 5, played in the supplied order                 |
| Direction        | Uppercase `H` (horizontal) or `V` (vertical)         |
| Brick contents   | Exactly three symbols chosen from `@`, `^`, `~`, `*` |

Separate dimensions and bricks with whitespace; keep each brick token together. Do not enter a separate brick count.

`H@~~` places symbols left to right; `V^**` places them top to bottom. Invalid configuration displays a message and prompts again. A valid brick that cannot fit on the board ends the game when its turn to spawn arrives.

## Commands and turns

Commands are case-insensitive, and whitespace between commands is ignored.

| Command | Action                                |
| ------- | ------------------------------------- |
| `L`     | Attempt to move one column left       |
| `R`     | Attempt to move one column right      |
| `D`     | Drop to the lowest available position |

Each input line uses one turn. The first two valid command characters are processed in order. Gravity then attempts to move the brick down one row. If it cannot move down, the brick locks, matches clear, and the next brick attempts to spawn.

| Input                    | Result before gravity                                 |
| ------------------------ | ----------------------------------------------------- |
| `L R` or `lr`            | Move left, then right                                 |
| `RR`                     | Attempt two moves right                               |
| `DR`                     | Drop, then attempt to move right before locking       |
| `XLR`                    | Ignore `X`; move left, then right                     |
| `LRD`                    | Process `L` and `R`; ignore the third valid command   |
| `XY`                     | Display an invalid-input message; make no player move |
| Blank or whitespace only | Make no player move, without an error message         |

**Invalid-only and blank input both use a turn and apply gravity.** Invalid characters mixed with valid commands are ignored without an error message.

## Board and matching rules

- `.` represents an empty cell.
- Bricks spawn at the top, centered horizontally. Horizontal bricks use the left of two possible positions when exact centering is impossible.
- Bricks move as a unit. Board edges and locked cells block movement. A blocked sideways command leaves the brick in place.
- Matches are checked after locking, not while a brick is moving.
- Horizontal and vertical runs of at least three identical symbols clear simultaneously. Longer runs and intersections clear too; diagonals do not.
- Clearing leaves gaps. Previously locked symbols do not fall, and there are no gravity cascades.

The final board is displayed before `Game Over.`, including when a brick cannot spawn because it does not fit or its starting cells are occupied.

## Restart and exit

After game over:

- Enter `S` to start over with a fresh configuration.
- Enter `Q` to quit.

Menu choices are case-insensitive. Other menu input prompts again.

At an input prompt, Ctrl+C exits with a farewell message. Closed standard input also exits cleanly, including when piped input runs out of lines. Run the application again to start another session.

## Development and testing

Install test dependencies:

```sh
python -m pip install -r requirements.txt
```

Run the complete suite:

```sh
python -m pytest
```

Run the real-process tests with piped stdin:

```sh
python -m pytest test/test_end_to_end.py
```

Report line and branch coverage in the terminal:

```sh
python -m pytest --cov=app --cov-branch --cov-report=term-missing
```

Tests cover configuration parsing, validation messages, movement, matching, turn sequencing, restart behavior, and input interruption. Subprocess cases cover invalid setup recovery, blank and invalid commands, blocked spawning, and closed input.

## Code structure

| Module              | Responsibility                                       |
| ------------------- | ---------------------------------------------------- |
| `app/main.py`       | Entry point and restart/quit loop                    |
| `app/controller.py` | Terminal input parsing, prompting, and rendering     |
| `app/game.py`       | Board rules, matching, and turn sequencing           |
| `app/brick.py`      | Brick parsing and validation                         |
| `app/config.py`     | `GameConfig`: named dimensions and a tuple of bricks |
| `app/models.py`     | `Command`, `Direction`, and the `Cell` named tuple   |
| `app/constants.py`  | Symbols, empty-cell marker, and size/count limits    |
| `app/errors.py`     | Configuration and brick-validation exceptions        |
| `app/user_input.py` | EOF and Ctrl+C handling at prompts                   |
| `test/`             | Unit, integration, and end-to-end tests              |

The controller calls `Game.start()` once and passes validated commands to `Game.step()` until `is_over` is true. The game owns gravity, locking, clearing, brick progression, and completion; it contains no terminal input or printing.

`GameConfig` requires named constructor arguments and prevents field reassignment. Its brick collection is a tuple; individual `Brick` objects remain mutable.
