# Match-3 Brick Game

A terminal-based falling-brick game. Bricks contain `@`, `#`, `~`, and `*` symbols and can be horizontal (`H`) or vertical (`V`).

## Requirements

- Python 3.10 or newer (required by pytest 9)

The game itself uses only the Python standard library. The test suite uses pytest.

## Run the game

From the project root:

```powershell
python -m app.main
```

Enter the board height, board width, and one or more bricks on a single line:

```text
5 7 H@~~ V#**
```

Each brick starts with its direction:

- `H` for horizontal
- `V` for vertical

Each brick must contain at least three supported symbols: `@`, `#`, `~`, or `*`.

## Commands

Enter up to two commands per frame:

- `L` — move left
- `R` — move right
- `D` — drop to the lowest available position

For example, `LR` moves left, then right during one frame.

## Run tests

```powershell
python -m pip install -r requirements.txt
python -m pytest
```

## Test with coverage

From the project root, run:

```powershell
python -m pytest --cov=app --cov-branch --cov-report=term-missing
```

This uses the `pytest-cov` plugin from `requirements.txt` to measure line and
branch coverage in `app/`. The report appears in the terminal and lists
uncovered lines. No HTML report is generated.

## Project layout

```text
app/
  brick.py    # Brick parsing and validation
  errors.py   # Custom exceptions
  game.py     # Board and game rules
  main.py     # Terminal program entry point

test/
  test_brick.py
  test_game.py
```
