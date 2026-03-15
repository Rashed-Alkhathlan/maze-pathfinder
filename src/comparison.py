from __future__ import annotations

import random
from secrets import randbelow

from src.algorithms import ALGORITHMS
from src.algorithms.common import SolverResult
from src.maze import Maze


def normalize_seed(seed: int | None) -> int:
    return seed if seed is not None else randbelow(10_000_000_000)


def evaluate_optimality(results: list[SolverResult]) -> None:
    baseline = next((result for result in results if result.algorithm == "Dijkstra"), None)
    if baseline is None or not baseline.status.found:
        for result in results:
            result.status.actual_optimal = None
        return

    optimal_cost = baseline.metrics.path_cost
    for result in results:
        if not result.status.found:
            result.status.actual_optimal = None
            continue
        result.status.actual_optimal = result.metrics.path_cost == optimal_cost


def candidate_count_for_size(size: int) -> int:
    if size <= 18:
        return 7
    if size <= 30:
        return 5
    if size <= 45:
        return 4
    return 3


def candidate_seeds(base_seed: int, count: int) -> list[int]:
    seeds = [base_seed]
    rng = random.Random(base_seed)
    seen = {base_seed}

    while len(seeds) < count:
        candidate = rng.randrange(10_000_000_000)
        if candidate in seen:
            continue
        seen.add(candidate)
        seeds.append(candidate)
    return seeds


def divergence_score(results: list[SolverResult], *, weighted: bool) -> float:
    solved = [result for result in results if result.status.found]
    if len(solved) < 2:
        return float("-inf")

    by_name = {result.algorithm: result for result in solved}
    explored = [result.metrics.nodes_explored for result in solved]
    lengths = [result.metrics.path_length for result in solved]
    costs = [result.metrics.path_cost for result in solved]
    score = 0.0
    score += (max(explored) - min(explored)) * 0.6
    score += (max(lengths) - min(lengths)) * 10
    score += (max(costs) - min(costs)) * 8
    score += (len(set(lengths)) - 1) * 60
    score += (len(set(costs)) - 1) * 70

    dijkstra = by_name.get("Dijkstra")
    if dijkstra is None:
        return score

    bfs = by_name.get("BFS")
    dfs = by_name.get("DFS")
    a_star = by_name.get("A*")

    if bfs is not None:
        score += abs(bfs.metrics.nodes_explored - dijkstra.metrics.nodes_explored) * 0.4
        score += abs(bfs.metrics.path_length - dijkstra.metrics.path_length) * 8
        if weighted:
            score += max(0, bfs.metrics.path_cost - dijkstra.metrics.path_cost) * 16
            if bfs.metrics.path_cost == dijkstra.metrics.path_cost:
                score -= 120

    if dfs is not None:
        score += abs(dfs.metrics.nodes_explored - dijkstra.metrics.nodes_explored) * 0.4
        score += max(0, dfs.metrics.path_length - dijkstra.metrics.path_length) * 10
        score += max(0, dfs.metrics.path_cost - dijkstra.metrics.path_cost) * 10

    if a_star is not None:
        score += max(0, dijkstra.metrics.nodes_explored - a_star.metrics.nodes_explored) * 1.1
        score += abs(a_star.metrics.path_length - dijkstra.metrics.path_length) * 4

    if weighted:
        distinct_nonoptimal_costs = len(
            {
                result.metrics.path_cost
                for result in solved
                if result.algorithm in {"BFS", "DFS"}
                and result.metrics.path_cost > dijkstra.metrics.path_cost
            }
        )
        score += distinct_nonoptimal_costs * 90

    return score


def generate_ranked_candidate(
    *,
    size: int,
    weighted: bool,
    loop_factor: float,
    seed: int,
) -> tuple[Maze, list[SolverResult]]:
    maze = Maze.generate(
        size=size,
        weighted=weighted,
        seed=seed,
        loop_factor=loop_factor,
    )
    results = [solver(maze) for _, solver in ALGORITHMS]
    evaluate_optimality(results)
    return maze, results


def run_algorithm_suite(
    *,
    size: int = 15,
    seed: int | None = None,
    weighted: bool = False,
    loop_factor: float = 0.18,
) -> dict:
    resolved_seed = normalize_seed(seed)
    best_maze = None
    best_results = None
    best_score = float("-inf")

    for candidate_seed in candidate_seeds(resolved_seed, candidate_count_for_size(size)):
        maze, results = generate_ranked_candidate(
            size=size,
            weighted=weighted,
            loop_factor=loop_factor,
            seed=candidate_seed,
        )
        score = divergence_score(results, weighted=weighted)
        if score > best_score:
            best_maze = maze
            best_results = results
            best_score = score

    best_maze.seed = resolved_seed

    return {
        "seed": resolved_seed,
        "maze": best_maze.to_dict(),
        "algorithms": [result.to_payload() for result in best_results],
    }
