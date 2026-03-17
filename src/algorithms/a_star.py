import heapq
from time import perf_counter

from src.algorithms.common import record_event, result_from_search


def heuristic(node, goal):
    """Return Manhattan distance between two maze cells."""
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])


def solve(maze):
    """Solve the maze with A* search.

    A* combines two pieces of information for every frontier node:

    - the exact cost already spent to reach that node
    - a heuristic estimate of the remaining cost to the goal

    Those values are added together into a priority score. The algorithm always
    expands the node with the smallest score first which usually focuses the
    search in the direction of the goal more aggressively than Dijkstra.

    This implementation has:

    - `open_set`: a min-heap of `(priority, path_cost_so_far, node)`
    - `best_cost`: the cheapest known real cost to each discovered node
    - `parents`: back-pointers used to rebuild the final path
    - `expanded`: nodes that have already been permanently processed

    When a neighbor is found with a cheaper cost than before, its parent and
    best known cost are updated and it is pushed back into the heap with a new
    priority. Once the goal is popped from the heap, the best path has been
    found. Because the heuristic here is admissible, A* retains optimality
    while usually exploring fewer nodes than Dijkstra.
    """
    
    start = maze.start
    goal = maze.goal
    open_set = [(heuristic(start, goal), 0, start)]
    parents = {start: None}
    best_cost = {start: 0}
    expanded = set()
    events = []
    nodes_explored = 0
    frontier_peak = 1
    runtime_start = perf_counter()
    found = False

    while open_set:
        _, cost, node = heapq.heappop(open_set)
        if node in expanded:
            continue

        expanded.add(node)
        nodes_explored += 1
        record_event(events, "expand", node, frontier_size=len(open_set))

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
            heapq.heappush(open_set, (new_cost + heuristic(neighbor, goal), new_cost, neighbor))
            frontier_peak = max(frontier_peak, len(open_set))
            record_event(events, "discover", neighbor, frontier_size=len(open_set))

    return result_from_search(
        algorithm="A*",
        maze=maze,
        events=events,
        parents=parents,
        found=found,
        nodes_explored=nodes_explored,
        frontier_peak=frontier_peak,
        runtime_start=runtime_start,
        guaranteed_optimal=True,
        optimality_note="A* is optimal here because the Manhattan heuristic is admissible.",
    )
