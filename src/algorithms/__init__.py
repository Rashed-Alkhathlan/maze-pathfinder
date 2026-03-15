from src.algorithms.a_star import solve as solve_a_star
from src.algorithms.bfs import solve as solve_bfs
from src.algorithms.dfs import solve as solve_dfs
from src.algorithms.dijkstra import solve as solve_dijkstra


ALGORITHMS = (
    ("BFS", solve_bfs),
    ("DFS", solve_dfs),
    ("Dijkstra", solve_dijkstra),
    ("A*", solve_a_star),
)

__all__ = ["ALGORITHMS", "solve_a_star", "solve_bfs", "solve_dfs", "solve_dijkstra"]
