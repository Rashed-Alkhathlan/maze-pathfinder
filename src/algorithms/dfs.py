from time import perf_counter

from src.algorithms.common import record_event, result_from_search


def solve(maze):
    """Solve the maze with depth-first search.

    DFS pushes forward along one branch as far as it can before backtracking.
    It uses a stack, so the most recently discovered neighbor is explored next.
    This gives it a very different personality from BFS: DFS can reach the goal
    quickly if it happens to guess the right corridor, but it can also dive deep
    into poor routes before correcting course.

    The algorithm stores:

    - `stack`: the active frontier of nodes to explore next
    - `parents`: the first predecessor that reached each node

    As with BFS, once a node has a parent it is treated as visited and is not
    pushed again. That keeps the traversal simple and guarantees termination on
    mazes with loops.

    DFS is useful here as a contrast algorithm. It is usually lightweight and
    easy to implement, but it does not guarantee the fewest moves or the lowest
    total cost, even in an unweighted maze.
    """
    start = maze.start
    goal = maze.goal
    stack = [start]
    parents = {start: None}
    events = []
    nodes_explored = 0
    frontier_peak = 1
    runtime_start = perf_counter()
    found = False

    while stack:
        node = stack.pop()
        nodes_explored += 1
        record_event(events, "expand", node, frontier_size=len(stack))

        if node == goal:
            found = True
            break

        neighbors = maze.neighbors(node)
        for neighbor in reversed(neighbors):
            if neighbor in parents:
                continue
            parents[neighbor] = node
            stack.append(neighbor)
            frontier_peak = max(frontier_peak, len(stack))
            record_event(events, "discover", neighbor, frontier_size=len(stack))

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
