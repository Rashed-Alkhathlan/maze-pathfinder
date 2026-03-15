from __future__ import annotations

from time import perf_counter

from src.algorithms.common import TraceEvent, result_from_search
from src.maze import Maze


def solve(maze: Maze):
    stack = [maze.start]
    parents = {maze.start: None}
    events: list[TraceEvent] = []
    nodes_explored = 0
    frontier_peak = 1
    runtime_start = perf_counter()
    found = False

    while stack:
        row, col = stack.pop()
        nodes_explored += 1
        events.append(TraceEvent(kind="expand", row=row, col=col, frontier_size=len(stack)))

        if (row, col) == maze.goal:
            found = True
            break

        neighbors = maze.neighbors((row, col))
        for neighbor in reversed(neighbors):
            if neighbor in parents:
                continue
            parents[neighbor] = (row, col)
            stack.append(neighbor)
            frontier_peak = max(frontier_peak, len(stack))
            events.append(
                TraceEvent(
                    kind="discover",
                    row=neighbor[0],
                    col=neighbor[1],
                    frontier_size=len(stack),
                )
            )

    return result_from_search(
        algorithm="DFS",
        maze=maze,
        events=events,
        parents=parents,
        found=found,
        nodes_explored=nodes_explored,
        frontier_peak=frontier_peak,
        runtime_start=runtime_start,
        guaranteed_optimal=False,
        optimality_note="DFS is not guaranteed to find an optimal path.",
    )
