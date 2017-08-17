# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Domino shuffling algorithm on Aztec diamond graphs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script samples a random domino tiling of an Aztec diamond graph
with uniform probability.

Matplotlib is slower than cairo but it renders much better images.

Usage: python aztec_matplotlib.py [-s] [-o] [-f]

Optional arguments:
    -s    size of the image.
    -o    order of the Aztec diamond graph.
    -f    output file.

:copyright (c) 2015 by Zhao Liang.
"""

import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mps
import aztec


def draw_with_matplotlib(az, size, filename):
    """Draw current tiling of az to a png file with matplotlib.
        az:
            an instance of the AztecDiamond class.
        size:
            image size in pixels, e.g. size = 600 means 600x600
        filename:
            output filename, must be a .png image.
    """
    fig = plt.figure(figsize=(size/100.0, size/100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], aspect=1)
    ax.axis([-az.order-1, az.order+1, -az.order-1, az.order+1])
    ax.axis('off')
    linewidth = fig.dpi * fig.get_figwidth() / (20.0 * (az.order + 1))
    
    for i, j in az.cells:
        if az.is_black(i, j) and az.tile[(i, j)] is not None:
            if az.tile[(i, j)] == 'n':
                p = mps.Rectangle((i-1, j), 2, 1, fc='r')
            if az.tile[(i, j)] == 's':
                p = mps.Rectangle((i, j), 2, 1, fc='y')
            if az.tile[(i, j)] == 'w':
                p = mps.Rectangle((i, j), 1, 2, fc='b')
            if az.tile[(i, j)] == 'e':
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

    az = aztec.AztecDiamond(0)
    for _ in range(args.order):
        az = az.delete().slide().create()
    draw_with_matplotlib(az, args.size, args.filename)


if __name__ == '__main__':
    main()
