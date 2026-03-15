import unittest

from src.maze import Maze


def graph_stats(maze: Maze) -> tuple[int, int]:
    nodes = 0
    edges = 0
    for row in range(maze.grid_size):
        for col in range(maze.grid_size):
            if maze.is_wall(row, col):
                continue
            nodes += 1
            for next_row, next_col in ((row + 1, col), (row, col + 1)):
                if maze.in_bounds(next_row, next_col) and not maze.is_wall(next_row, next_col):
                    edges += 1
    return nodes, edges


class MazeGenerationTests(unittest.TestCase):
    def test_seeded_generation_is_reproducible(self) -> None:
        first = Maze.generate(size=8, seed=42, weighted=False)
        second = Maze.generate(size=8, seed=42, weighted=False)

        self.assertEqual(first.grid, second.grid)
        self.assertEqual(first.start, second.start)
        self.assertEqual(first.goal, second.goal)

    def test_seeded_weight_placement_is_reproducible(self) -> None:
        first = Maze.generate(size=8, seed=99, weighted=True)
        second = Maze.generate(size=8, seed=99, weighted=True)

        self.assertEqual(first.grid, second.grid)
        self.assertTrue(any(value > 1 for row in first.grid for value in row))

    def test_zero_loop_factor_keeps_maze_tree_shaped(self) -> None:
        maze = Maze.generate(size=8, seed=7, weighted=False, loop_factor=0.0)

        nodes, edges = graph_stats(maze)
        self.assertEqual(edges, nodes - 1)

    def test_loop_factor_adds_cycles(self) -> None:
        maze = Maze.generate(size=8, seed=7, weighted=False, loop_factor=0.18)

        nodes, edges = graph_stats(maze)
        self.assertGreater(edges, nodes - 1)
        self.assertAlmostEqual(maze.loop_factor, 0.18)


if __name__ == "__main__":
    unittest.main()
