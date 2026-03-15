from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable


Coordinate = tuple[int, int]


@dataclass(slots=True)
class Maze:
    logical_size: int
    grid: list[list[int]]
    weighted: bool = False
    seed: int | None = None
    loop_factor: float = 0.18

    WALL = 1
    PASSAGE = 0

    @classmethod
    def generate(
        cls,
        size: int = 15,
        *,
        weighted: bool = False,
        seed: int | None = None,
        loop_factor: float = 0.18,
        weight_probability: float = 0.3,
        weight_range: tuple[int, int] = (2, 10),
    ) -> "Maze":
        if size < 2:
            raise ValueError("maze size must be at least 2")
        if not 0 <= loop_factor <= 1:
            raise ValueError("loop_factor must be between 0 and 1")

        grid_size = 2 * size + 1
        grid = [[cls.WALL for _ in range(grid_size)] for _ in range(grid_size)]
        rng = random.Random(seed)
        stack: list[Coordinate] = [(1, 1)]
        grid[1][1] = cls.PASSAGE

        while stack:
            row, col = stack[-1]
            neighbors = cls._carvable_neighbors(grid, row, col, grid_size)

            if not neighbors:
                stack.pop()
                continue

            next_row, next_col = rng.choice(neighbors)
            wall_row = (row + next_row) // 2
            wall_col = (col + next_col) // 2

            grid[wall_row][wall_col] = cls.PASSAGE
            grid[next_row][next_col] = cls.PASSAGE
            stack.append((next_row, next_col))

        maze = cls(
            logical_size=size,
            grid=grid,
            weighted=weighted,
            seed=seed,
            loop_factor=loop_factor,
        )
        maze.add_loops(rng=rng, factor=loop_factor)
        if weighted:
            maze.apply_weights(
                rng=rng,
                probability=weight_probability,
                weight_range=weight_range,
            )
        return maze

    @classmethod
    def from_grid(
        cls,
        grid: Iterable[Iterable[int]],
        *,
        weighted: bool = False,
        seed: int | None = None,
        loop_factor: float = 0.0,
    ) -> "Maze":
        rows = [list(row) for row in grid]
        if not rows or any(len(row) != len(rows[0]) for row in rows):
            raise ValueError("maze grid must be a non-empty rectangle")
        if len(rows) != len(rows[0]):
            raise ValueError("maze grid must be square")
        logical_size = (len(rows) - 1) // 2
        return cls(
            logical_size=logical_size,
            grid=rows,
            weighted=weighted,
            seed=seed,
            loop_factor=loop_factor,
        )

    @staticmethod
    def _carvable_neighbors(
        grid: list[list[int]],
        row: int,
        col: int,
        grid_size: int,
    ) -> list[Coordinate]:
        neighbors: list[Coordinate] = []
        for d_row, d_col in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            next_row = row + d_row
            next_col = col + d_col
            if not (0 < next_row < grid_size - 1 and 0 < next_col < grid_size - 1):
                continue
            if grid[next_row][next_col] == Maze.WALL:
                neighbors.append((next_row, next_col))
        return neighbors

    @property
    def grid_size(self) -> int:
        return len(self.grid)

    @property
    def start(self) -> Coordinate:
        return (1, 1)

    @property
    def goal(self) -> Coordinate:
        end = self.grid_size - 2
        return (end, end)

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.grid_size and 0 <= col < self.grid_size

    def is_wall(self, row: int, col: int) -> bool:
        return self.grid[row][col] == self.WALL

    def neighbors(self, node: Coordinate) -> list[Coordinate]:
        row, col = node
        candidates = ((row, col + 1), (row + 1, col), (row, col - 1), (row - 1, col))
        return [
            (next_row, next_col)
            for next_row, next_col in candidates
            if self.in_bounds(next_row, next_col) and not self.is_wall(next_row, next_col)
        ]

    def movement_cost(self, node: Coordinate) -> int:
        row, col = node
        value = self.grid[row][col]
        return value if value > 1 else 1

    def path_cost(self, path: list[Coordinate]) -> int:
        if not path:
            return 0
        return sum(self.movement_cost(node) for node in path[1:])

    def add_loops(self, *, rng: random.Random, factor: float) -> int:
        if factor <= 0:
            return 0

        candidates: list[Coordinate] = []
        for row in range(1, self.grid_size - 1):
            for col in range(1, self.grid_size - 1):
                if self.grid[row][col] != self.WALL:
                    continue
                if row % 2 == 1 and col % 2 == 0:
                    if self.grid[row][col - 1] != self.WALL and self.grid[row][col + 1] != self.WALL:
                        candidates.append((row, col))
                elif row % 2 == 0 and col % 2 == 1:
                    if self.grid[row - 1][col] != self.WALL and self.grid[row + 1][col] != self.WALL:
                        candidates.append((row, col))

        if not candidates:
            return 0

        loop_count = max(1, round(len(candidates) * factor))
        loop_count = min(loop_count, len(candidates))
        for row, col in rng.sample(candidates, loop_count):
            self.grid[row][col] = self.PASSAGE
        return loop_count

    def apply_weights(
        self,
        *,
        rng: random.Random,
        probability: float = 0.3,
        weight_range: tuple[int, int] = (2, 10),
    ) -> None:
        low, high = weight_range
        for row in range(1, self.grid_size - 1):
            for col in range(1, self.grid_size - 1):
                if (row, col) in (self.start, self.goal):
                    continue
                if self.grid[row][col] == self.PASSAGE and rng.random() < probability:
                    self.grid[row][col] = rng.randint(low, high)

    def max_weight(self) -> int:
        return max((value for row in self.grid for value in row if value > 1), default=1)

    def to_dict(self) -> dict:
        return {
            "logical_size": self.logical_size,
            "grid_size": self.grid_size,
            "grid": [row[:] for row in self.grid],
            "weighted": self.weighted,
            "seed": self.seed,
            "loop_factor": self.loop_factor,
            "start": list(self.start),
            "goal": list(self.goal),
            "max_weight": self.max_weight(),
        }
