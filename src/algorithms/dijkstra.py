from __future__ import annotations

import heapq
from time import perf_counter

from src.algorithms.common import TraceEvent, result_from_search
from src.maze import Maze


def solve(maze: Maze):
    heap: list[tuple[int, int, int]] = [(0, maze.start[0], maze.start[1])]
    parents = {maze.start: None}
    best_cost = {maze.start: 0}
    expanded: set[tuple[int, int]] = set()
    events: list[TraceEvent] = []
    nodes_explored = 0
    frontier_peak = 1
    runtime_start = perf_counter()
    found = False

    while heap:
        cost, row, col = heapq.heappop(heap)
        node = (row, col)
        if node in expanded:
            continue

        expanded.add(node)
        nodes_explored += 1
        events.append(TraceEvent(kind="expand", row=row, col=col, frontier_size=len(heap)))

        if node == maze.goal:
            found = True
            break

        for neighbor in maze.neighbors(node):
            tentative_cost = cost + maze.movement_cost(neighbor)
            if tentative_cost >= best_cost.get(neighbor, float("inf")):
                continue

            best_cost[neighbor] = tentative_cost
            parents[neighbor] = node
            heapq.heappush(heap, (tentative_cost, neighbor[0], neighbor[1]))
            frontier_peak = max(frontier_peak, len(heap))
            events.append(
                TraceEvent(
                    kind="discover",
                    row=neighbor[0],
                    col=neighbor[1],
                    frontier_size=len(heap),
                )
            )

    return result_from_search(
        algorithm="Dijkstra",
        maze=maze,
        events=events,
        parents=parents,
        found=found,
        nodes_explored=nodes_explored,
        frontier_peak=frontier_peak,
        runtime_start=runtime_start,
        guaranteed_optimal=True,
        optimality_note="Dijkstra guarantees the minimum path cost with non-negative weights.",
    )
