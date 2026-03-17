# Maze Solver Observatory

An app that generates mazes in Python, solves the same maze with
BFS, DFS, Dijkstra, and A*, and visualizes all four runs side by side in the
browser.

## Overview

This project is built to compare search behavior, not just final answers.

- One seeded maze is generated per run and shared by all algorithms
- Weighted and unweighted mazes are both supported
- The frontend animates each solver in real time on its own canvas
- The comparison view highlights explored nodes, runtime, path length, path
  cost, and whether a path was found
- The backend keeps the solver logic in Python end to end

## Quick Start

| Task | Command |
| --- | --- |
| Install dependencies | `python3 -m pip install -r requirements.txt` |
| Run the app | `python3 -m uvicorn src.app:app --reload` |
| Run tests | `python3 -m unittest discover -s tests` |

Open `http://127.0.0.1:8000` after starting the server.

The API test is skipped automatically if `fastapi` and `httpx` are not
installed.

## Algorithm Guide

For a detailed walkthrough of the solver code, including the shared helper layer
and the maze methods the solvers depend on, see
[Algorithm Explanation Guide](src/algorithms/explanation.md).

## What You Can Explore

- Seeded maze generation for reproducible runs
- Braided mazes with multiple valid routes
- Weighted cells that make cheapest path and shortest path diverge
- Side-by-side BFS, DFS, Dijkstra, and A* playback
- A shared API response from `/api/run` that powers the visualizer

## Project Layout

| Path | Purpose |
| --- | --- |
| `src/maze/maze.py` | Deterministic maze generation plus traversal and cost helpers |
| `src/algorithms/` | BFS, DFS, Dijkstra, A*, shared solver models, and explanation docs |
| `src/comparison.py` | Run orchestration and solver comparison logic |
| `src/app.py` | FastAPI app and `/api/run` endpoint |
| `src/static/` | Browser UI, styling, and canvas animation |
| `tests/` | Maze, solver, and API verification |
