import os
import random
import time

import numpy as np

class Maze:
    """
    Recursive Backtracking Maze Firas style idk bro.
    """
    def __init__(self, size, print_each_step=False):
        self._print = print_each_step

        self.size = 2 * size + 1
        # we represent both cells and paths in this array
        # so size is not just width x height but rather (2 * size + 1)
        self.maze = np.ones((self.size, self.size), dtype=int)

    def _check_neighbors(self, y, x, offset=2):
        # a neighbor is valid iff
        # 1) in grid (i.e > 0)
        # 2) its value = 1 (not visited)

        neighbors = []

        # check up (y decreases)
        up = y - offset
        if up > 0:
            if self.maze[up][x] == 1:
                neighbors.append((up, x, 'up'))

        # check down (y increases)
        down = y + offset
        if down < self.size - 1:
            if self.maze[down][x] == 1:
                neighbors.append((down, x, 'down'))

        # check left (x decreases)
        left = x - offset
        if left > 0:
            if self.maze[y][left] == 1:
                neighbors.append((y, left, 'left'))

        # check right (x increases)
        right = x + offset
        if right < self.size - 1:
            if self.maze[y][right] == 1:
                neighbors.append((y, right, 'right'))

        return neighbors

    def generate_maze_(self):
        stack = []
        offset = 2 # because we have walls, we need to look 2 indices away and not 1

        y, x = 1, 1
        #initially the first cell is carved
        self.maze[y][x] = 0
        stack.append((y, x))

        while len(stack) > 0:
            #--------
            if self._print:
                self.print_maze()
                time.sleep(0.001)
            #--------

            y, x = stack[-1] # look at last carved cell
            cell_neighbors = self._check_neighbors(y, x, offset)

            if len(cell_neighbors) > 0:
                #if there are neighbors continue
                y_neighbor, x_neighbor, direction = random.choice(cell_neighbors)
            else:
                #else, backtrack
                stack.pop()
                continue

            #carve the neighbor
            self.maze[y_neighbor][x_neighbor] = 0

            #push neighbor to stack
            stack.append((y_neighbor, x_neighbor))

            #carve the wall between the 2 cells
            if direction == 'up' or direction == 'down':
                wall_position = (y + y_neighbor) // 2 # if 3 and 5 then wall is on 4
                self.maze[wall_position][x] = 0

            if direction == 'left' or direction == 'right':
                wall_position = (x + x_neighbor) // 2
                self.maze[y][wall_position] = 0

    def print_maze(self):
        print("\033[H", end="")

        for row in self.maze:
            line = ""
            for cell in row:
                if cell == 1:
                    line += "██"
                else:
                    line += "  "
            print(line)
        print("\n", end="", flush=True)