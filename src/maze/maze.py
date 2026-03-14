import random
import time
import numpy as np

class Maze:
    """
    Recursive Backtracking Maze my style idk.
    """
    def __init__(self, size, weighted=False, print_each_step=False):
        self.is_weighted = weighted
        self._print = print_each_step
        self.fully_generated = False

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

        self.fully_generated = True
        if self.fully_generated and self.is_weighted:
            self.make_weighted_(probability=0.3, weight_range=(2, 10))


    def print_maze(self):
        print("\033[H", end="")

        if not self.is_weighted:
            for row in self.maze:
                line = ""
                for cell in row:
                    if cell == 1:
                        line += "██"
                    else:
                        line += "  "
                print(line)
            print("\n", end="", flush=True)

        else:
            start = (1, 1)
            goal = (self.size - 2, self.size - 2)

            # collect current weights in maze
            weights = self.maze[self.maze > 1]
            max_weight = weights.max() if len(weights) > 0 else 2
            min_weight = weights.min() if len(weights) > 0 else 2

            # low -> high weight colors
            # green -> yellow -> orange -> red
            color_scale = [236, 238, 240, 242, 244, 246, 248]


            for y, row in enumerate(self.maze):
                line = ""
                for x, cell in enumerate(row):

                    # walls
                    if cell == 1:
                        line += "\033[90m██\033[0m"

                    # start
                    elif (y, x) == start:
                        line += "\033[44mST\033[0m"

                    # goal
                    elif (y, x) == goal:
                        line += "\033[45mGL\033[0m"

                    # normal unweighted path
                    elif cell == 0:
                        line += "  "

                    # weighted path
                    else:
                        if max_weight == min_weight:
                            color_idx = 0
                        else:
                            normalized = (cell - min_weight) / (max_weight - min_weight)
                            color_idx = int(normalized * (len(color_scale) - 1))

                        bg = color_scale[color_idx]
                        line += f"\033[48;5;{bg}m  \033[0m"

                print(line)

            print("\n", end="", flush=True)


    def make_weighted_(self, probability:float, weight_range: tuple):
        """
        Parameters
        ----------
        probability: (0, 1.0)
        weight_range: must be in the range of (2, inf)

        Returns
        -------
        None, makes the maze weighted inplace
        """

        if not self.fully_generated:
            raise Exception("how do you want to add weights if maze is not complete .-.")

        low, high = weight_range
        start = (1, 1)
        goal = (self.size - 2, self.size - 2)

        for row in range(1, self.size - 1):
            for column in range(1, self.size - 1):
                if (row, column) == start or (row, column) == goal:
                    continue

                if self.maze[row][column] == 0:
                    if np.random.random() < probability:
                        random_weight = np.random.randint(low, high + 1)
                        self.maze[row][column] = random_weight
