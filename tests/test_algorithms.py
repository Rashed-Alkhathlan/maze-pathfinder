import unittest

from src.algorithms.a_star import solve as solve_a_star
from src.algorithms.bfs import solve as solve_bfs
from src.algorithms.dfs import solve as solve_dfs
from src.algorithms.dijkstra import solve as solve_dijkstra
from src.maze import Maze


OPEN_GRID = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
]

DFS_DETOUR_GRID = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
]

WEIGHTED_GRID = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 9, 9, 9, 9, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 2, 1, 0, 1],
    [1, 0, 1, 2, 1, 0, 1],
    [1, 0, 0, 2, 2, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
]

DISCONNECTED_GRID = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1],
    [1, 0, 1, 1, 1, 1, 1],
    [1, 0, 1, 1, 1, 1, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
]


def assert_valid_path(test_case: unittest.TestCase, maze: Maze, path: list[tuple[int, int]]) -> None:
    test_case.assertEqual(path[0], maze.start)
    test_case.assertEqual(path[-1], maze.goal)
    for current, nxt in zip(path, path[1:]):
        test_case.assertIn(nxt, maze.neighbors(current))


class AlgorithmTests(unittest.TestCase):
    def test_bfs_finds_shortest_hop_path_in_unweighted_maze(self) -> None:
        maze = Maze.from_grid(OPEN_GRID)
        result = solve_bfs(maze)

        self.assertTrue(result.status.found)
        self.assertEqual(result.metrics.path_length, 8)
        assert_valid_path(self, maze, result.path)

    def test_dfs_returns_valid_but_not_necessarily_shortest_path(self) -> None:
        maze = Maze.from_grid(DFS_DETOUR_GRID)
        bfs_result = solve_bfs(maze)
        dfs_result = solve_dfs(maze)

        self.assertTrue(dfs_result.status.found)
        assert_valid_path(self, maze, dfs_result.path)
        self.assertGreater(dfs_result.metrics.path_length, bfs_result.metrics.path_length)

    def test_dijkstra_finds_minimum_cost_path_on_weighted_maze(self) -> None:
        maze = Maze.from_grid(WEIGHTED_GRID, weighted=True)
        bfs_result = solve_bfs(maze)
        dijkstra_result = solve_dijkstra(maze)

        self.assertTrue(dijkstra_result.status.found)
        self.assertEqual(dijkstra_result.metrics.path_cost, 10)
        self.assertLess(dijkstra_result.metrics.path_cost, bfs_result.metrics.path_cost)
        assert_valid_path(self, maze, dijkstra_result.path)

    def test_a_star_matches_dijkstra_cost_on_weighted_maze(self) -> None:
        maze = Maze.from_grid(WEIGHTED_GRID, weighted=True)
        dijkstra_result = solve_dijkstra(maze)
        a_star_result = solve_a_star(maze)

        self.assertTrue(a_star_result.status.found)
        self.assertEqual(a_star_result.metrics.path_cost, dijkstra_result.metrics.path_cost)
        assert_valid_path(self, maze, a_star_result.path)

    def test_all_solvers_report_not_found_on_disconnected_maze(self) -> None:
        maze = Maze.from_grid(DISCONNECTED_GRID)

        for solver in (solve_bfs, solve_dfs, solve_dijkstra, solve_a_star):
            result = solver(maze)
            self.assertFalse(result.status.found)
            self.assertEqual(result.path, [])
            self.assertEqual(result.metrics.path_cost, 0)


if __name__ == "__main__":
    unittest.main()
