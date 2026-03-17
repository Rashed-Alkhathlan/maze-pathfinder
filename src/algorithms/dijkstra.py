import heapq
from time import perf_counter

from src.algorithms.common import record_event, result_from_search


def solve(maze):
    """Solve the maze with Dijkstra's algorithm.

    Dijkstra expands nodes in order of the cheapest total cost seen so far from
    the start. Unlike BFS, it respects weighted cells, so a longer route can be
    preferred if its total movement cost is lower.

    The heap stores `(path_cost_so_far, node)`. Each time the cheapest entry is
    popped, that node becomes the next confirmed shortest-cost state. For every
    reachable neighbor, the algorithm computes a new candidate cost:

    current path cost + movement cost of entering the neighbor

    If that candidate is better than any cost seen previously, the neighbor's
    parent and best known cost are updated and the neighbor is pushed into the
    heap. Once the goal is removed from the heap, the cheapest path to it is
    known.

    In this project, Dijkstra is the baseline for weighted mazes because it is
    guaranteed to find the minimum-cost route as long as all edge weights are
    non-negative, which they are here.
    """
    start = maze.start
    goal = maze.goal
    queue = [(0, start)]
    parents = {start: None}
    best_cost = {start: 0}
    expanded = set()
    events = []
    nodes_explored = 0
    frontier_peak = 1
    runtime_start = perf_counter()
    found = False

    while queue:
        cost, node = heapq.heappop(queue)
        if node in expanded:
            continue

        expanded.add(node)
        nodes_explored += 1
        record_event(events, "expand", node, frontier_size=len(queue))

        if node == goal:
            found = True
            break

        for neighbor in maze.neighbors(node):
            new_cost = cost + maze.movement_cost(neighbor)
            known_cost = best_cost.get(neighbor)
            if known_cost is not None and new_cost >= known_cost:
                continue

            best_cost[neighbor] = new_cost
            parents[neighbor] = node
            heapq.heappush(queue, (new_cost, neighbor))
            frontier_peak = max(frontier_peak, len(queue))
            record_event(events, "discover", neighbor, frontier_size=len(queue))

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
