"""Curated maze scenarios for best / worst / average case analysis per algorithm.

Each scenario uses a specific seed and maze configuration found via exhaustive
search over thousands of candidates to *guarantee* the described behaviour.
"""

from __future__ import annotations

SCENARIOS: dict[tuple[str, str], dict] = {
    # ------------------------------------------------------------------
    # DFS - uses unweighted mazes with loops (loop_factor=0.30) so that
    # multiple paths exist and DFS can diverge from the BFS-optimal one.
    # ------------------------------------------------------------------
    ("DFS", "best"): {
        "size": 15,
        "seed": 36,
        "weighted": False,
        "loop_factor": 0.30,
        "description": (
            "DFS explores only 57 nodes and finds a path of length 56, "
            "matching BFS's optimal path exactly. The maze layout causes "
            "DFS's stack ordering to head straight toward the goal."
        ),
    },
    ("DFS", "worst"): {
        "size": 15,
        "seed": 2511,
        "weighted": False,
        "loop_factor": 0.30,
        "description": (
            "DFS finds a path of length 220 versus BFS's optimal 60, "
            "a 3.7x inflation. DFS dives into every dead-end corridor "
            "before finally reaching the goal, exploring 275 nodes."
        ),
    },
    ("DFS", "average"): {
        "size": 15,
        "seed": 1517,
        "weighted": False,
        "loop_factor": 0.30,
        "description": (
            "DFS explores 69 nodes and finds a path of length 68 versus "
            "BFS's optimal 56, a typical 21% deviation on a moderately "
            "connected maze."
        ),
    },
    # ------------------------------------------------------------------
    # BFS - uses *weighted* mazes to expose BFS's inability to account
    # for movement costs (it minimises hop count, not total cost).
    # ------------------------------------------------------------------
    ("BFS", "best"): {
        "size": 15,
        "seed": 2621,
        "weighted": True,
        "loop_factor": 0.18,
        "description": (
            "BFS finds a path costing 194, identical to Dijkstra's "
            "optimal cost. By luck, the shortest-hop path also happens "
            "to be the cheapest on this particular maze."
        ),
    },
    ("BFS", "worst"): {
        "size": 15,
        "seed": 961,
        "weighted": True,
        "loop_factor": 0.18,
        "description": (
            "BFS finds a path costing 215 versus Dijkstra's optimal 117, "
            "an 84% overpay. BFS picks the fewest-hop route which "
            "crosses many expensive weighted cells."
        ),
    },
    ("BFS", "average"): {
        "size": 15,
        "seed": 1976,
        "weighted": True,
        "loop_factor": 0.18,
        "description": (
            "BFS path costs 133 versus Dijkstra's 120, an 11% overhead "
            "that is typical for moderately weighted mazes."
        ),
    },
    # ------------------------------------------------------------------
    # A* - compared against Dijkstra to show how much the Manhattan
    # heuristic helps (or fails to help) in different maze layouts.
    # ------------------------------------------------------------------
    ("A*", "best"): {
        "size": 20,
        "seed": 2722,
        "weighted": True,
        "loop_factor": 0.18,
        "description": (
            "A* explores only 299 nodes versus Dijkstra's 671. The "
            "heuristic saves 55% of the work. The maze layout lets "
            "A* focus tightly on a corridor leading toward the goal."
        ),
    },
    ("A*", "worst"): {
        "size": 20,
        "seed": 47,
        "weighted": True,
        "loop_factor": 0.18,
        "description": (
            "A* explores all 864 reachable nodes, exactly the same as "
            "Dijkstra. Heavy weights and winding corridors make the "
            "Manhattan heuristic provide zero advantage."
        ),
    },
    ("A*", "average"): {
        "size": 20,
        "seed": 3,
        "weighted": True,
        "loop_factor": 0.18,
        "description": (
            "A* explores 731 nodes versus Dijkstra's 823, an 11% saving "
            "that is typical for weighted mazes of this size."
        ),
    },
    # ------------------------------------------------------------------
    # Dijkstra - measured by how much of the maze must be explored before
    # the optimal path to the goal is confirmed.
    # ------------------------------------------------------------------
    ("Dijkstra", "best"): {
        "size": 20,
        "seed": 4051,
        "weighted": True,
        "loop_factor": 0.18,
        "description": (
            "Dijkstra explores only 442 of 864 reachable nodes (51%) "
            "before confirming the optimal path. Favourable weight "
            "placement lets it lock in the cheapest route early."
        ),
    },
    ("Dijkstra", "worst"): {
        "size": 20,
        "seed": 43,
        "weighted": True,
        "loop_factor": 0.18,
        "description": (
            "Dijkstra must explore all 864 reachable nodes. It cannot "
            "confirm the goal's optimal cost until every alternative "
            "has been checked."
        ),
    },
    ("Dijkstra", "average"): {
        "size": 20,
        "seed": 2130,
        "weighted": True,
        "loop_factor": 0.18,
        "description": (
            "Dijkstra explores 837 of 864 reachable nodes (97%), "
            "typical for large weighted mazes where most of the graph "
            "must be settled before the goal is finalised."
        ),
    },
}


ALGORITHM_NAMES = ("BFS", "DFS", "Dijkstra", "A*")
CASE_NAMES = ("best", "worst", "average")


def get_scenario(algorithm: str, case: str) -> dict:
    """Return a scenario definition or raise ValueError."""
    key = (algorithm, case)
    if key not in SCENARIOS:
        raise ValueError(
            f"Unknown scenario ({algorithm!r}, {case!r}). "
            f"Valid algorithms: {ALGORITHM_NAMES}, cases: {CASE_NAMES}"
        )
    return SCENARIOS[key]


def all_scenarios() -> list[dict]:
    """Return the full list of scenarios for the frontend."""
    result = []
    for (algorithm, case), config in SCENARIOS.items():
        result.append({
            "algorithm": algorithm,
            "case": case,
            **config,
        })
    return result
