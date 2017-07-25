# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Domino shuffling algorithm on Aztec diamond graphs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script samples a random domino tiling of an Aztec diamond graph
with uniform probability.

Matplotlib is slower than cairo but it renders better images.

Usage: python aztec_matplotlib.py [-s] [-o] [-f]

Optional arguments:
    -s    size of the image.
    -o    order of the Aztec diamond graph.
    -f    output file.

:copyright (c) 2015 by Zhao Liang.
"""

import argparse
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mps


class AztecDiamond(object):
    """Use a dict to represent a tiling of an Aztec diamond graph.
    Items in the dict are of the form {cell: type} where a cell is a
    1x1 unit square and is specified by the coordinate of its left bottom
    corner. Each cell has five possible types: 'n', 's', 'w', 'e', None,
    here None means it's an empty cell.

    Be careful that one should always start from the boundary when
    deleting or filling blocks, this is an implicit but important
    part in the algorithm.
    """

    def __init__(self, n):
        """Create an Aztec diamond graph of order n with an empty tiling."""
        self.order = n

        self.cells = []
        for j in range(-n, n):
            k = min(n+1+j, n-j)
            for i in range(-k, k):
                self.cells.append((i, j))

        self.tile = {cell: None for cell in self.cells}

    @staticmethod
    def block(i, j):
        """Return the 2x2 block with its bottom-left cell at (i, j)."""
        return [(i, j), (i+1, j), (i, j+1), (i+1, j+1)]

    def is_black(self, i, j):
        """Check if cell (i, j) is colored black.
        Note that the chessboard is colored in the fashion that the
        leftmost cell in the top row is white.
        """
        return (i + j + self.order) % 2 == 1

    def check_block(self, i, j, dominoes):
        """Check whether a block is filled with dominoes of given orientations."""
        return all(self.tile[cell] == fill for cell, fill in zip(self.block(i, j), dominoes))

    def fill_block(self, i, j, dominoes):
        """Fill a block with two parallel dominoes of given orientations."""
        for cell, fill in zip(self.block(i, j), dominoes):
            self.tile[cell] = fill

    def delete(self):
        """Delete all bad blocks in a tiling.
        A block is called bad if it contains a pair of parallel dominoes that
        have orientations toward each other.
        """
        for i, j in self.cells:
            try:
                if (self.check_block(i, j, ['n', 'n', 's', 's'])
                        or self.check_block(i, j, ['e', 'w', 'e', 'w'])):
                    self.fill_block(i, j, [None]*4)
            except KeyError:
                pass
        return self

    def slide(self):
        """Move all dominoes one step according to their orientations."""
        new_board = AztecDiamond(self.order + 1)
        for (i, j) in self.cells:
            if self.tile[(i, j)] == 'n':
                new_board.tile[(i, j+1)] = 'n'
            if self.tile[(i, j)] == 's':
                new_board.tile[(i, j-1)] = 's'
            if self.tile[(i, j)] == 'w':
                new_board.tile[(i-1, j)] = 'w'
            if self.tile[(i, j)] == 'e':
                new_board.tile[(i+1, j)] = 'e'
        return new_board

    def create(self):
        """Fill all holes with pairs of dominoes that leaving each other.
        This is a somewhat subtle step since the new Aztec graph returned
        by the sliding step is placed on a different chessboard which is
        colored in the opposite fashion!
        """
        for i, j in self.cells:
            try:
                if self.check_block(i, j, [None]*4):
                    if random.random() > 0.5:
                        self.fill_block(i, j, ['s', 's', 'n', 'n'])
                    else:
                        self.fill_block(i, j, ['w', 'e', 'w', 'e'])
            except KeyError:
                pass
        return self

    def render(self, size, filename):
        """Draw current tiling to a png file.
        size:
            image size in pixels, e.g. size = 600 means 600x600
        filename:
            output filename, must be a .png image.
        """
        fig = plt.figure(figsize=(size/100.0, size/100.0), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1], aspect=1)
        ax.axis([-self.order-1, self.order+1, -self.order-1, self.order+1])
        ax.axis('off')
        linewidth = fig.dpi * fig.get_figwidth() / (20.0 * (self.order + 1))

        for i, j in self.cells:
            if self.is_black(i, j) and self.tile[(i, j)] is not None:
                if self.tile[(i, j)] == 'n':
                    p = mps.Rectangle((i-1, j), 2, 1, fc='r')
                if self.tile[(i, j)] == 's':
                    p = mps.Rectangle((i, j), 2, 1, fc='y')
                if self.tile[(i, j)] == 'w':
                    p = mps.Rectangle((i, j), 1, 2, fc='b')
                if self.tile[(i, j)] == 'e':
                    p = mps.Rectangle((i, j-1), 1, 2, fc='g')

                p.set_linewidth(linewidth)
                p.set_edgecolor('w')
                ax.add_patch(p)

        fig.savefig(filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-size', metavar='s', type=int,
                        default=800, help='image size')
    parser.add_argument('-order', metavar='o', type=int,
                        default=60, help='order of az graph')
    parser.add_argument('-filename', metavar='f', type=str,
                        default='randomtiling.png', help='output filename')
    args = parser.parse_args()

    az = AztecDiamond(0)
    for _ in range(args.order):
        az = az.delete().slide().create()
    az.render(args.size, args.filename)


if __name__ == '__main__':
    main()
