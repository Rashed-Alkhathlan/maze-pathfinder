# Maze Solver Explanation Guide

## Purpose And Reading Guide

This file explains the current solver implementation in:

- `src/algorithms/bfs.py`
- `src/algorithms/dfs.py`
- `src/algorithms/dijkstra.py`
- `src/algorithms/a_star.py`
- `src/algorithms/common.py`

It also explains the solver-facing parts of `src/maze/maze.py` that those files
depend on.

The goal is not to teach a generic textbook version of each algorithm. The goal
is to explain the exact code that exists in this repository right now:

- what each function takes as input
- what each function returns
- what the local variables mean
- how control flows line by line
- how the data structures change while the search runs

The line references below match the current code at the time this document was
written. If the Python files change later, the explanations will still be useful
conceptually, but the exact line numbers may drift.

## Shared Concepts Used By All Solvers

### What A Maze Node Is

In this project, a maze node is a coordinate tuple:

```python
(row, col)
```

Example:

```python
(1, 1)
```

means row `1`, column `1` in the maze grid.

All four solvers move from one coordinate to another by calling:

```python
maze.neighbors(node)
```

### What `start` And `goal` Mean

Every solver reads:

```python
start = maze.start
goal = maze.goal
```

For the current `Maze` class:

- `start` is always `(1, 1)`
- `goal` is always `(grid_size - 2, grid_size - 2)`

So the maze starts near the top-left inner corner and ends near the bottom-right
inner corner.

### What A Parent Map Is

A parent map is a dictionary that remembers how we first or best reached a node.

Example:

```python
parents = {
    (1, 1): None,
    (1, 2): (1, 1),
    (1, 3): (1, 2),
}
```

This says:

- `(1, 1)` is the start, so it has no parent
- `(1, 2)` was reached from `(1, 1)`
- `(1, 3)` was reached from `(1, 2)`

At the end, the code walks backward from the goal through this map to rebuild
the final path.

### What `events` Means

Each solver records animation events in a list called `events`.

These events are later used by the web UI to replay the solving process.

There are three event kinds:

- `discover`: a node was added to the frontier
- `expand`: a node was removed from the frontier and actively processed
- `path`: the final chosen path was written out after the search finished

### What The Metrics Mean

Every solver eventually returns metrics with these meanings:

- `nodes_explored`: how many nodes were actually expanded
- `frontier_peak`: the largest size reached by the queue, stack, or heap
- `path_length`: number of moves from start to goal
- `path_cost`: total movement cost of the path, excluding the start node
- `runtime_ms`: search runtime in milliseconds

### Weighted Vs Unweighted Mazes

In an unweighted maze:

- normal passage cells have cost `1`
- `path_length` and `path_cost` end up equal

In a weighted maze:

- some passage cells contain numbers greater than `1`
- entering those cells costs more
- BFS and DFS still ignore weight when choosing where to go
- Dijkstra and A* do use weight when deciding which route is better

That is why BFS can find a path with fewer steps but a worse total cost than
Dijkstra or A*.

## Shared Example Maze

The examples below reuse this small maze:

```python
example_grid = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 6, 6, 6, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
]
```

Interpretation:

- `1` means wall
- `0` means ordinary passage
- `6` means a weighted passage that costs `6` to enter

Visual version:

```text
#######
#S666.#
#.###.#
#...#.#
###.#.#
#....G#
#######
```

Here:

- `S` is the start at `(1, 1)`
- `G` is the goal at `(5, 5)`

This maze is useful because:

- there is a top route with high weights
- there is a lower route with cheaper cells
- BFS and DFS can prefer the top route because of traversal order
- Dijkstra and A* can prefer the cheaper route because of cost awareness

## Maze API Primer For Solver Readers

This section only covers the parts of `Maze` that the solvers actually use.

### `start` In `maze.py`

```python
@property
def start(self) -> Coordinate:
    return (1, 1)
```

- Input: -
- Return: the start coordinate tuple
- Meaning: every solver begins here

### `goal` In `maze.py`

```python
@property
def goal(self) -> Coordinate:
    end = self.grid_size - 2
    return (end, end)
```

- Input: -
- Return: the goal coordinate tuple
- Meaning: every solver tries to reach this node

`end = self.grid_size - 2` skips the solid wall border around the maze.

### `neighbors(node)` In `maze.py`

```python
def neighbors(self, node: Coordinate) -> list[Coordinate]:
    row, col = node
    candidates = ((row, col + 1), (row + 1, col), (row, col - 1), (row - 1, col))
    return [
        (next_row, next_col)
        for next_row, next_col in candidates
        if self.in_bounds(next_row, next_col) and not self.is_wall(next_row, next_col)
    ]
```

- Input: one node coordinate
- Return: a list of reachable neighboring coordinates
- Neighbor order: right, down, left, up

That order matters. BFS and DFS use it directly, so it can change which equally
valid path they find first.

Example:

```python
maze.neighbors((1, 1))
```

on the shared example returns:

```python
[(1, 2), (2, 1)]
```

The right neighbor appears before the down neighbor.

### `movement_cost(node)` In `maze.py`

```python
def movement_cost(self, node: Coordinate) -> int:
    row, col = node
    value = self.grid[row][col]
    return value if value > 1 else 1
```

- Input: one node coordinate
- Return: the cost of entering that node

Rules:

- wall values are never passed in because walls are filtered out earlier
- ordinary passage `0` costs `1`
- weighted passage like `6` costs `6`

Example:

```python
maze.movement_cost((1, 2))  # 6
maze.movement_cost((3, 2))  # 1
```

### `path_cost(path)` In `maze.py`

```python
def path_cost(self, path: list[Coordinate]) -> int:
    if not path:
        return 0
    return sum(self.movement_cost(node) for node in path[1:])
```

- Input: a full path list
- Return: total cost of the path

Important detail: `path[1:]` skips the start node. The code treats cost as the
price of entering later cells, not the price of standing on the start.

### Grid Value Meaning

In solver terms:

- `1` means wall, not traversable
- `0` means ordinary passage, traversable with cost `1`
- any value greater than `1` means weighted passage, traversable with that cost

## `common.py` Walkthrough

The file `common.py` holds the shared structures and helper functions that all
solvers use.

### `TraceEvent`

```python
@dataclass(slots=True)
class TraceEvent:
    kind: EventKind
    row: int
    col: int
    frontier_size: int

    def to_dict(self) -> dict[str, int | str]:
        return {
            "kind": self.kind,
            "row": self.row,
            "col": self.col,
            "frontier_size": self.frontier_size,
        }
```

What it is:

- a container for one animation event

What it stores:

- `kind`: `discover`, `expand`, or `path`
- `row`, `col`: where the event happened
- `frontier_size`: how large the frontier was at that moment

What `to_dict()` returns:

- a normal Python dictionary ready to be serialized for the frontend

### `SolverMetrics`

This dataclass stores the numeric results of a run.

Field meaning:

- `nodes_explored`: number of expansions
- `frontier_peak`: max queue, stack, or heap size
- `path_length`: moves from start to goal
- `path_cost`: total path cost
- `runtime_ms`: runtime in milliseconds

Its `to_dict()` method mirrors the dataclass fields and rounds runtime before serialization.

### `SolverStatus`

This dataclass stores non-numeric result information.

Field meaning:

- `found`: whether the goal was reached
- `guaranteed_optimal`: whether the algorithm is theoretically optimal in the
  current conditions
- `actual_optimal`: runtime comparison flag filled later by comparison logic
- `optimality_note`: human-readable explanation

### `SolverResult`

This is the complete return object from every solver.

It groups together:

- `algorithm`: name such as `"BFS"` or `"A*"`
- `path`: final coordinate list
- `events`: trace events
- `metrics`: a `SolverMetrics` instance
- `status`: a `SolverStatus` instance

Its `to_payload()` method converts everything into JSON-safe structures:

- tuples become lists
- dataclasses become dictionaries

### `reconstruct_path`

```python
def reconstruct_path(
    parents: dict[Coordinate, Coordinate | None],
    goal: Coordinate,
) -> list[Coordinate]:
    path: list[Coordinate] = []
    node: Coordinate | None = goal
    while node is not None:
        path.append(node)
        node = parents.get(node)
    path.reverse()
    return path
```

What it takes:

- `parents`: a map from node to parent
- `goal`: the goal coordinate

What it returns:

- a path list from start to goal

How it works:

1. Start from `goal`.
2. Append the current node to `path`.
3. Move to that node's parent.
4. Repeat until `None`.
5. Reverse the list because it was collected backward.

Example:

```python
parents = {
    (1, 1): None,
    (1, 2): (1, 1),
    (1, 3): (1, 2),
}
reconstruct_path(parents, (1, 3))
```

Result:

```python
[(1, 1), (1, 2), (1, 3)]
```

### `record_event`

This helper turns a node tuple into a `TraceEvent` and appends it to the event
list.

Inputs:

- `events`: the event list to mutate
- `kind`: event type
- `node`: `(row, col)`
- `frontier_size`: size of frontier at this moment

Return:

- `None`

The function exists so every solver does not need to repeat the same event
construction code.

### `record_path`

This helper writes a `path` event for every node in the final chosen path.

Inputs:

- `events`: the event list to mutate
- `path`: list of coordinates

Return:

- `None`

It simply loops through the path and calls `record_event(..., "path", ...)`.

### `result_from_search`

This is the final assembly function that every solver calls before returning.

Inputs:

- `algorithm`: display name
- `maze`: maze object
- `events`: collected events
- `parents`: parent map
- `found`: whether the goal was reached
- `nodes_explored`: expansion count
- `frontier_peak`: peak frontier size
- `runtime_start`: start time from `perf_counter()`
- `guaranteed_optimal`: theory-level optimality flag
- `optimality_note`: human-readable explanation

Return:

- one `SolverResult`

Step by step:

1. `runtime_ms = (perf_counter() - runtime_start) * 1000`
   computes elapsed time in milliseconds.
2. `path = reconstruct_path(...) if found else []`
   rebuilds the path only if the goal was actually reached.
3. `if found: record_path(events, path)`
   appends final path events so the UI can animate the winning route.
4. `metrics = SolverMetrics(...)`
   packages the numeric results.
5. `status = SolverStatus(...)`
   packages the non-numeric state.
6. `return SolverResult(...)`
   returns the complete solver output.

## BFS Walkthrough

Source file: `src/algorithms/bfs.py`

### What `solve(maze)` Takes

- Input: one `Maze` object
- Output: one `SolverResult`

### Core Idea

Breadth-first search explores in rings around the start.

The first time BFS reaches a node, it has reached it using the fewest number of
moves. That is why BFS is optimal on unweighted mazes.

### Important Local Variables

- `queue`: `deque` of discovered nodes waiting to be expanded
- `parents`: remembers the first path to each node
- `events`: animation trace
- `nodes_explored`: expansion counter
- `frontier_peak`: largest queue size seen
- `runtime_start`: starting timestamp
- `found`: whether goal was reached

### Line-By-Line Walkthrough

#### Imports

```python
from collections import deque
from time import perf_counter

from src.algorithms.common import record_event, result_from_search
```

- `deque` gives efficient queue operations from the left side
- `perf_counter` measures runtime
- `record_event` and `result_from_search` are shared helpers

#### Setup

```python
start = maze.start
goal = maze.goal
queue = deque([start])
parents = {start: None}
events = []
nodes_explored = 0
frontier_peak = 1
runtime_start = perf_counter()
found = False
```

What each line means:

- `start = maze.start`: read the start coordinate from the maze
- `goal = maze.goal`: read the goal coordinate
- `queue = deque([start])`: initialize the BFS frontier with the start node
- `parents = {start: None}`: mark the start as already discovered
- `events = []`: prepare to store trace events
- `nodes_explored = 0`: no nodes have been expanded yet
- `frontier_peak = 1`: the queue currently contains one node
- `runtime_start = perf_counter()`: remember when the search began
- `found = False`: assume failure until the goal is seen

#### Main Loop

```python
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
```

What happens here:

- `while queue:` keeps going until there are no more nodes to try
- `queue.popleft()` removes the oldest discovered node
- `nodes_explored += 1` counts that expansion
- `record_event(..., "expand", ...)` logs the expansion
- `if node == goal:` stops immediately when the goal is expanded
- `maze.neighbors(node)` gets reachable adjacent cells
- `if neighbor in parents:` skips already discovered nodes
- `parents[neighbor] = node` remembers how that neighbor was reached
- `queue.append(neighbor)` adds the neighbor to the back of the queue
- `frontier_peak = max(...)` updates the max queue size
- `record_event(..., "discover", ...)` logs the discovery

#### Return

The final `result_from_search(...)` call packages everything into a
`SolverResult`.

Important arguments:

- `algorithm="BFS"` labels the result
- `guaranteed_optimal=not maze.weighted` says BFS is only guaranteed optimal
  when weights are not active
- `optimality_note=...` explains that guarantee in plain language

### Worked Example

Using the shared example maze, the start node is `(1, 1)`.

Initial state:

```python
queue = deque([(1, 1)])
parents = {(1, 1): None}
```

Step 1:

- pop `(1, 1)`
- neighbors are `[(1, 2), (2, 1)]`
- add both in that order

Now:

```python
queue = deque([(1, 2), (2, 1)])
parents = {
    (1, 1): None,
    (1, 2): (1, 1),
    (2, 1): (1, 1),
}
```

Step 2:

- pop `(1, 2)` first because it entered the queue first
- this pushes BFS toward the top route before the lower route

That ordering continues layer by layer. Because the top route reaches the goal
in the same number of steps as the cheaper lower route, BFS can lock in the top
route first even though it has a much higher total cost.

### What BFS Guarantees

- On an unweighted maze, BFS guarantees the fewest moves.
- On a weighted maze, BFS does not guarantee the cheapest total cost.

## DFS Walkthrough

Source file: `src/algorithms/dfs.py`

### What `solve(maze)` Takes

- Input: one `Maze` object
- Output: one `SolverResult`

### Core Idea

Depth-first search goes as far as it can down one branch before backing up.

It does not compare path costs and it does not guarantee the shortest route. It
is mainly useful here as a contrast algorithm because its behavior can be very
different from BFS.

### Important Local Variables

- `stack`: list used as a LIFO frontier
- `parents`: remembers the first time each node was discovered
- `events`: animation trace
- `nodes_explored`, `frontier_peak`, `runtime_start`, `found`: same roles as BFS

### Line-By-Line Walkthrough

#### Imports

- `perf_counter` measures runtime
- shared helpers are imported from `common.py`

#### Setup

```python
start = maze.start
goal = maze.goal
stack = [start]
parents = {start: None}
events = []
nodes_explored = 0
frontier_peak = 1
runtime_start = perf_counter()
found = False
```

This setup is almost the same as BFS except:

- the frontier is a plain list called `stack`
- nodes will be removed with `pop()`, so the newest node is explored next

#### Main Loop

```python
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
```

Important detail:

- `maze.neighbors(node)` returns neighbors in the order right, down, left, up
- DFS loops over `reversed(neighbors)`
- then it `append`s those neighbors to a stack
- because stacks pop the last pushed item first, reversing here preserves a
  predictable traversal order

For the start node in the shared maze:

- original neighbors: `[(1, 2), (2, 1)]`
- reversed order: `[(2, 1), (1, 2)]`
- append down, then append right
- `stack.pop()` takes `(1, 2)` next

So DFS also heads toward the top branch first in this implementation.

#### Return

The return block mirrors BFS, except:

- `algorithm="DFS"`
- `guaranteed_optimal=False`
- the optimality note explicitly says DFS is not guaranteed to find an optimal
  path

### Worked Example

Initial state:

```python
stack = [(1, 1)]
```

After expanding `(1, 1)`:

```python
neighbors = [(1, 2), (2, 1)]
reversed(neighbors) = [(2, 1), (1, 2)]
stack = [(2, 1), (1, 2)]
```

Next step:

- `stack.pop()` returns `(1, 2)`
- DFS continues deeper into the top branch instead of exploring layer by layer

That is why DFS can sometimes reach a solution quickly, but it can also commit
to a bad branch for a long time before correcting.

### What DFS Guarantees

- DFS guarantees termination on these mazes because discovered nodes are never
  pushed twice.
- DFS does not guarantee the fewest moves.
- DFS does not guarantee the minimum total cost.

## Dijkstra Walkthrough

Source file: `src/algorithms/dijkstra.py`

### What `solve(maze)` Takes

- Input: one `Maze` object
- Output: one `SolverResult`

### Core Idea

Dijkstra always expands the frontier node with the cheapest known path cost from
the start.

That makes it the correct baseline for weighted mazes with non-negative costs.

### Important Local Variables

- `queue`: min-heap of `(cost_so_far, node)`
- `parents`: best-known predecessor for each node
- `best_cost`: cheapest known cost to each discovered node
- `expanded`: nodes whose cheapest cost has been finalized
- `events`, `nodes_explored`, `frontier_peak`, `runtime_start`, `found`

### Line-By-Line Walkthrough

#### Imports

- `heapq` provides heap push and pop operations
- `perf_counter` times the search
- shared helpers come from `common.py`

#### Setup

```python
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
```

Meaning of the important lines:

- `queue = [(0, start)]` says the start node is reachable with cost `0`
- `best_cost = {start: 0}` stores that same fact in dictionary form
- `expanded = set()` will prevent reprocessing finalized nodes

#### Main Loop

```python
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
```

What each logical step means:

- `heapq.heappop(queue)` removes the lowest-cost frontier entry
- `if node in expanded:` skips stale heap entries for nodes that were already
  finalized earlier
- `expanded.add(node)` marks this node as done
- `new_cost = cost + maze.movement_cost(neighbor)` calculates the total cost of
  reaching the neighbor through the current node
- `known_cost = best_cost.get(neighbor)` looks up the cheapest known cost so far
- `if known_cost is not None and new_cost >= known_cost:` ignores worse or equal
  routes
- `best_cost[neighbor] = new_cost` records the improved cost
- `parents[neighbor] = node` records the improved parent
- `heapq.heappush(...)` adds the neighbor back into the heap with its new cost

#### Return

The return block labels this result as `"Dijkstra"` and marks it as guaranteed
optimal because all movement costs in this project are non-negative.

### Worked Example

Start:

```python
queue = [(0, (1, 1))]
best_cost = {(1, 1): 0}
```

After expanding `(1, 1)` in the shared example:

- neighbor `(1, 2)` gets cost `6`
- neighbor `(2, 1)` gets cost `1`

Now:

```python
queue = [(1, (2, 1)), (6, (1, 2))]
best_cost = {
    (1, 1): 0,
    (1, 2): 6,
    (2, 1): 1,
}
```

The heap pops `(2, 1)` next, not `(1, 2)`, because `1 < 6`.

That single choice shows the whole personality of Dijkstra: it prefers the
cheaper path even when the expensive path was discovered first.

### What Dijkstra Guarantees

- It guarantees the minimum total path cost.
- It does not specifically optimize for fewest moves.
- In an unweighted maze, its cheapest path also becomes a shortest-step path
  because every move costs the same.

## A* Walkthrough

Source file: `src/algorithms/a_star.py`

### What `heuristic(node, goal)` Takes And Returns

- Inputs: `node`, `goal`
- Return: Manhattan distance as an integer

Code:

```python
def heuristic(node, goal):
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])
```

Why this works:

- the maze only allows right, down, left, and up movement
- Manhattan distance counts how many row and column moves are still needed
- it never overestimates the true remaining cost when every move costs at least
  `1`

That last property is what makes the heuristic admissible.

### What `solve(maze)` Takes

- Input: one `Maze` object
- Output: one `SolverResult`

### Core Idea

A* combines:

- `g`: the real cost already paid from start to the current node
- `h`: a heuristic estimate of remaining cost to the goal

It ranks frontier entries by:

```python
priority = g + h
```

So A* tries to keep the correctness of Dijkstra while steering more directly
toward the goal.

### Important Local Variables

- `open_set`: min-heap of `(priority, cost_so_far, node)`
- `parents`: best predecessor map
- `best_cost`: cheapest known real cost `g` to each node
- `expanded`: finalized nodes
- `events`, `nodes_explored`, `frontier_peak`, `runtime_start`, `found`

### What Each Tuple In `open_set` Means

Example heap entry:

```python
(11, 5, (3, 2))
```

This means:

- `11`: total priority `g + h`
- `5`: actual path cost so far `g`
- `(3, 2)`: the node

The node is popped based on the first value, but the second value is still kept
because the algorithm needs the real cost when expanding neighbors.

### Line-By-Line Walkthrough

#### Imports

- `heapq` is used for the frontier heap
- `perf_counter` measures runtime
- shared helpers come from `common.py`

#### Heuristic Function

```python
def heuristic(node, goal):
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])
```

Line meaning:

- `node[0] - goal[0]` is row distance
- `node[1] - goal[1]` is column distance
- `abs(...)` turns both into positive distances
- adding them gives Manhattan distance

#### Setup

```python
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
```

Most of this mirrors Dijkstra. The key difference is:

- `open_set = [(heuristic(start, goal), 0, start)]`

The start has:

- real cost `0`
- heuristic estimate `heuristic(start, goal)`
- priority equal to `0 + heuristic`

#### Main Loop

```python
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
```

Key details:

- `_, cost, node = heapq.heappop(open_set)` ignores the stored priority after it
  has done its job ordering the heap
- `cost` is the true `g` value, not the heuristic-augmented priority
- `new_cost` is computed exactly like Dijkstra
- the new heap priority is `new_cost + heuristic(neighbor, goal)`

So A* still tracks real cost correctly, but it chooses what to expand next using
the extra heuristic guidance.

#### Return

The return block marks A* as guaranteed optimal in this project because the
Manhattan heuristic is admissible under the maze's movement rules and cost
model.

### Worked Example

From the start in the shared example:

- `(1, 2)` has `g = 6`
- goal is `(5, 5)`
- `h((1, 2), goal) = |1 - 5| + |2 - 5| = 7`
- priority is `13`

For `(2, 1)`:

- `g = 1`
- `h((2, 1), goal) = |2 - 5| + |1 - 5| = 7`
- priority is `8`

So after the first expansion, the heap conceptually prefers:

```python
(8, 1, (2, 1))
```

over:

```python
(13, 6, (1, 2))
```

That pushes A* toward the cheaper lower route immediately, just like Dijkstra,
but later the heuristic can help it stay more focused on the goal than plain
Dijkstra.

### What A* Guarantees

- In this project, A* guarantees the minimum total path cost.
- It often explores fewer nodes than Dijkstra.
- If the heuristic were bad and overestimated true cost, optimality could break,
  but that does not happen with Manhattan distance here.

## Comparison Summary

| Algorithm | Search Order | Main Data Structure | Uses Weights? | Optimal Guarantee | Typical Tradeoff Here |
| --- | --- | --- | --- | --- | --- |
| BFS | Oldest discovered node first | `deque` queue | No | Yes, only on unweighted mazes | Simple and reliable for shortest steps, but can ignore expensive cells |
| DFS | Newest discovered node first | list stack | No | No | Can find a route quickly, but route quality can be poor |
| Dijkstra | Lowest real path cost first | heap of `(cost, node)` | Yes | Yes | Correct weighted baseline, but can explore broadly |
| A* | Lowest `g + h` priority first | heap of `(priority, cost, node)` | Yes | Yes, with this heuristic | Usually keeps Dijkstra's correctness while exploring less |

## Final Takeaway

All four solver files follow the same overall shape:

1. read `start` and `goal`
2. initialize a frontier and bookkeeping dictionaries
3. loop until the frontier is empty or the goal is found
4. record trace events while searching
5. call `result_from_search(...)` to package the answer

What changes from file to file is the rule used to choose the next frontier node:

- BFS chooses by discovery time
- DFS chooses by last-in-first-out order
- Dijkstra chooses by cheapest real cost
- A* chooses by cheapest real cost plus heuristic estimate

That one design choice is what creates the visible behavioral differences in the
visualizer and in the final metrics.
