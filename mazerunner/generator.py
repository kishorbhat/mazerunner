#!/usr/bin/env python3
from __future__ import print_function
import numpy as np


class Generator:
    def __init__(self, board_dimensions=(33, 33)):
        self.width = board_dimensions[1]
        self.height = board_dimensions[0]
        if self.width % 2 == 0:
            self.width += 1
        if self.height % 2 == 0:
            self.height += 1
        self.reset()

    def reset(self):
        self.maze = np.zeros((self.height, self.width), dtype=np.uint8)
        for x in range(self.maze.shape[0]):
            if x % 2 == 0:
                self.maze[x].fill(1)
        for y in range(self.maze.shape[1]):
            if y % 2 == 0:
                self.maze[:, y].fill(1)

        self.generated = False
        # both need to be odd numbers
        self.C = [(np.random.choice(range(3, self.height - 3, 2)),
                   np.random.choice(range(3, self.width - 3, 2)), 'W')]
        t = self.C[0]
        self.maze[t[0], t[1]] = 0
        self.maze[t[0] - 1, t[1]] = 0
        self.maze[t[0] + 1, t[1]] = 0
        self.maze[t[0], t[1] + 1] = 0
        self.maze[t[0], t[1] - 1] = 0
        self.maze_generator = self.step()
        self.maze[0].fill(1)
        self.maze[-1].fill(1)

    def step(self):
        while self.C:
            target = self.C[np.random.randint(0, len(self.C))]
            n = self.neighbours(target[0], target[1])
            np.random.shuffle(n)
            if not n:
                self.maze[target[0], target[1]] = 4
                if target[2] == 'S':
                    self.maze[target[0], target[1] - 1] = 4
                elif target[2] == 'N':
                    self.maze[target[0], target[1] + 1] = 4
                elif target[2] == 'E':
                    self.maze[target[0] - 1, target[1]] = 4
                elif target[2] == 'W':
                    self.maze[target[0] + 1, target[1]] = 4
                self.C.remove(target)
            else:
                # mark visited cells as 2
                new_cell = n.pop()
                self.maze[new_cell[0], new_cell[1]] = 2
                if new_cell[2] == 'S':
                    self.maze[new_cell[0], new_cell[1] - 1] = 2
                elif new_cell[2] == 'N':
                    self.maze[new_cell[0], new_cell[1] + 1] = 2
                elif new_cell[2] == 'E':
                    self.maze[new_cell[0] - 1, new_cell[1]] = 2
                elif new_cell[2] == 'W':
                    self.maze[new_cell[0] + 1, new_cell[1]] = 2

                self.C.append(new_cell)
            yield

    def neighbours(self, x, y, v=2):
        return [(nx, ny, d) for nx, ny, d in [(x, y + v, 'S'), (x, y - v, 'N'), (x + v, y, 'E'), (x - v, y, 'W')]
                if 1 <= nx < self.maze.shape[0] and 0 <= ny < self.maze.shape[1] and self.maze[nx, ny] <= 0]

    def gen(self):
        # do the next step in the maze generator
        while True:
            try:
                next(self.maze_generator)
            except StopIteration:
                for x in range(self.maze.shape[0]):
                    for y in range(self.maze.shape[1]):
                        if self.maze[x, y] != 1:
                            self.maze[x, y] = 0
                # put an exit in somewhere around the edge

                pos = np.random.choice(['top', 'left', 'right', 'bottom'])
                if pos == 'top':
                    ends = list(np.where(self.maze[:, 1] == 0)[0])
                    self.maze[np.random.choice(ends)][0] = 2
                elif pos == 'bottom':
                    ends = list(np.where(self.maze[:, -2] == 0)[0])
                    self.maze[np.random.choice(ends)][-1] = 2
                elif pos == 'left':
                    ends = list(np.where(self.maze[1] == 0)[0])
                    self.maze[0][np.random.choice(ends)] = 2
                else:
                    ends = list(np.where(self.maze[-2] == 0)[0])
                    self.maze[-1][np.random.choice(ends)] = 2
                return self.maze.copy()


def print_maze(maze, out=None):
    chars = {0: ' ', 1: '#', 2: 'X'}
    for row in maze:
        for c in row:
            print(chars[c], end='')
            if out is not None:
                out.write(chars[c])
        print()
        if out is not None:
            out.write("\n")


if __name__ == "__main__":
    # generate a random maze and print it
    import sys
    if len(sys.argv) != 4:
        sys.exit("Usage is: generator.py output_file width height")
    fname = sys.argv[1]
    width = int(sys.argv[2])
    height = int(sys.argv[3])
    gen = Generator((width, height))
    maze = gen.gen()

    with open('mazerunner/mazes/' + fname, 'w') as out:
        print_maze(maze, out)
