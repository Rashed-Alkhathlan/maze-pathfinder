# Maze Solver Observatory

Local FastAPI app for generating mazes in Python, solving them with BFS, DFS, Dijkstra, and A*, and visualizing all four traces side by side in the browser.

## What it does

- Generates one seeded maze per run with Python recursive backtracking
- Supports both unweighted and weighted mazes
- Runs all four algorithms against the exact same maze
- Animates each solver on its own canvas panel
- Compares explored nodes, peak frontier size, runtime, path length, path cost, completion, and actual optimality

`actual_optimal` means the algorithm matched Dijkstra's path cost on that specific maze.

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Run

```bash
uvicorn src.app:app --reload
```

Then open `http://127.0.0.1:8000`.

## Test

```bash
python3 -m unittest discover -s tests
```

The API test is skipped automatically if `fastapi` and `httpx` are not installed.

## Project layout

- `src/maze/maze.py`: deterministic maze generation and traversal helpers
- `src/algorithms/`: BFS, DFS, Dijkstra, A*, and shared solver result models
- `src/comparison.py`: run orchestration and Dijkstra baseline comparison
- `src/app.py`: FastAPI app and `/api/run` endpoint
- `src/static/`: browser UI, styling, and canvas animation
- `tests/`: maze, solver, and API verification
