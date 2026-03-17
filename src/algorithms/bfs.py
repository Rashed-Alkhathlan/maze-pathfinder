from collections import deque
from time import perf_counter

from src.algorithms.common import record_event, result_from_search


def solve(maze):
    """Solve the maze with breadth-first search.

    BFS explores the maze in layers radiating outward from the start. It uses a
    queue, so the first nodes discovered are the first nodes expanded. That
    means all cells at distance 1 are processed before any at distance 2, all
    cells at distance 2 before any at distance 3, and so on.

    The algorithm stores:

    - `queue`: the frontier of discovered but not yet expanded cells
    - `parents`: the first predecessor that reached each cell

    Because each cell is recorded in `parents` the first time it is seen, BFS
    never revisits it. That "first time seen" path is the shortest path in
    number of moves on an unweighted maze.

    Important limitation: BFS ignores movement weights. In a weighted maze it
    still finds a valid route, and often a short one in hop count, but not
    necessarily the cheapest route by total cost.
    """
    start = maze.start
    goal = maze.goal
    queue = deque([start])
    parents = {start: None}
    events = []
    nodes_explored = 0
    frontier_peak = 1
    runtime_start = perf_counter()
    found = False

    while queue:
        node = queue.popleft()
        nodes_explored += 1
        record_event(events, "expand", node, frontier_size=len(queue))

        if node == goal:
            found = True
            break

        for neighbor in maze.neighbors(node):
            if neighbor in parents:
                continue
            parents[neighbor] = node
            queue.append(neighbor)
            frontier_peak = max(frontier_peak, len(queue))
            record_event(events, "discover", neighbor, frontier_size=len(queue))

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
