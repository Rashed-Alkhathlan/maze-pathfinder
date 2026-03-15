from __future__ import annotations

from collections import deque
from time import perf_counter

from src.algorithms.common import TraceEvent, result_from_search
from src.maze import Maze


def solve(maze: Maze):
    queue = deque([maze.start])
    parents = {maze.start: None}
    events: list[TraceEvent] = []
    nodes_explored = 0
    frontier_peak = 1
    runtime_start = perf_counter()
    found = False

    while queue:
        row, col = queue.popleft()
        nodes_explored += 1
        events.append(TraceEvent(kind="expand", row=row, col=col, frontier_size=len(queue)))

        if (row, col) == maze.goal:
            found = True
            break

        for neighbor in maze.neighbors((row, col)):
            if neighbor in parents:
                continue
            parents[neighbor] = (row, col)
            queue.append(neighbor)
            frontier_peak = max(frontier_peak, len(queue))
            events.append(
                TraceEvent(
                    kind="discover",
                    row=neighbor[0],
                    col=neighbor[1],
                    frontier_size=len(queue),
                )
            )

    return result_from_search(
        algorithm="BFS",
        maze=maze,
        events=events,
        parents=parents,
        found=found,
        nodes_explored=nodes_explored,
        frontier_peak=frontier_peak,
        runtime_start=runtime_start,
        guaranteed_optimal=not maze.weighted,
        optimality_note=(
            "BFS is optimal for unweighted mazes only."
            if maze.weighted
            else "BFS guarantees the fewest moves on unweighted mazes."
        ),
    )
