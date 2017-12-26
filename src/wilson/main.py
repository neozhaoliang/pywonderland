# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Making GIF animations of various maze generation
and maze solving algorithms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage:
      python main.py [-size] [-scale]
                     [-margin] [-depth]
                     [-loop] [-filename]
Optional arguments:
    size: width and height of the maze (not the image), e.g. 101x81.
          should both be odd intergers.
    scale: the size of the image will be (width * scale) * (height * scale).
           In other words, each cell in the maze will occupy a square of
           (scale * scale) pixels in the image.
    margin: size of the border of the image.
    depth: color depth of the image (number of bits needed to represent all colors).
           This value determines the number of colors available in the image.
    loop: number of loops of the image, default to 0 (loop infinitely).
    filename: the output file.

Copyright (c) 2016 by Zhao Liang.
"""
import argparse
from colorsys import hls_to_rgb
from maze import Maze
from algorithms import (prim, random_dfs, kruskal, wilson, bfs, dfs, astar)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-size', type=str, default='121x97',
                        help='size of the maze, e.g. 101x81.')
    parser.add_argument('-margin', type=int, default=2,
                        help='border of the maze')
    parser.add_argument('-scale', type=int, default=5,
                        help='size of a cell in pixels')
    parser.add_argument('-loop', type=int, default=0,
                        help='number of loops of the animation, default to 0 (loop infinitely)')
    parser.add_argument('-depth', type=int, default=8,
                        help='an interger beteween 2-8 represents the color depth of the image,\
                        this parameter determines the size of the global color table.')
    parser.add_argument('-filename', type=str, default='wilson.gif',
                        help='output file name')
    args = parser.parse_args()

    width, height = [int(i) for i in args.size.split('x')]

    # define your favorite global color table here.
    mypalette = [0, 0, 0, 200, 200, 200, 255, 0, 255]

    # GIF files allows at most 256 colors in the global color table,
    # redundant colors will be discarded when the encoder is initialized.
    for i in range(256):
        rgb = hls_to_rgb((i / 360.0) % 1, 0.5, 1.0)
        mypalette += [int(round(255 * x)) for x in rgb]

    # you may use a binary image instance of PIL's Image class here as the mask image,
    # this image must preserve the connectivity of the grid graph.
    from gentext import generate_text_mask
    mask = generate_text_mask(width, height, 'UST', '../../resources/ubuntu.ttf', 60)
    maze = Maze(width, height, args.margin, mask=mask)
    canvas = maze.add_canvas(scale=args.scale, depth=args.depth, palette=mypalette,
                             loop=args.loop, filename=args.filename)

    # here we need to paint the blank background because the region that has not been
    # covered by any frame will be set to transparent by decoders.
    # Comment out this line and watch the result if you don't understand this.
    canvas.paint_background(wall_color=0)

    # pad one second delay, get ready!
    canvas.pad_delay_frame(delay=100)

    # you may adjust the `speed` parameter for different algorithms.
    canvas.set_control_params(delay=2, speed=50, trans_index=3,
                              wall_color=0, tree_color=1, path_color=2)

    start = (args.margin, args.margin)
    end = (width - args.margin - 1, height - args.margin - 1)

    # the maze generation animation.
    # try prim(maze, start) or kruskal(maze) or random_dfs(maze) here!
    wilson(maze, start)

    # pad three seconds delay to help to see the resulting maze clearly.
    canvas.pad_delay_frame(delay=300)

    # in the path finding animation the walls are unchanged throughout,
    # hence it's safe to use color 0 as the transparent color.
    canvas.set_control_params(delay=5, speed=30, trans_index=0, wall_color=0,
                              tree_color=0, path_color=2, fill_color=3)

    # the maze solving animation.
    # try dfs(maze, start, end) or astar(maze, start, end) here!
    bfs(maze, start, end)

    # pad five seconds delay to help to see the resulting path clearly.
    canvas.pad_delay_frame(delay=500)

    # finally finish the animation and close the file.
    canvas.save()


if __name__ == '__main__':
    main()
