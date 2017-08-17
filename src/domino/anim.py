# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make GIF Animations of the Domino Shuffling Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script requires ImageMagick be installed on your computer.
Windows users also need to set the variable `CONVERTER` below
to be the path to your `convert.exe`.

Here for efficiency considerings we use the cairocffi lib
instead of matplotlib to draw the frames of the animation.

Usage: python anim.py [-s] [-o] [-f]

Optional arguments:
    -s    size of the image.
    -o    order of the Aztec diamond graph.
    -f    output file. Must be a .gif file.

:copyright (c) 2015 by Zhao Liang.
"""

import os
import glob
import subprocess
import argparse
import cairocffi as cairo
import aztec


CONVERTER = 'convert'


def draw_with_cairo(az, size, extent, filename, bg_color=(1, 1, 1)):
    """
    Draw current tiling (might have holes) to a png image with cairo.
        az:
            an instance of the AztecDiamond class.
        size:
            image size in pixels, e.g. size = 600 means 600x600
        extent:
            range of the axis: [-extent, extent] x [-extent, extent]
        filename:
            output filename, must be a .png image.
        bg_color:
            background color, default to white.
            If set to None then transparent background will show through.
    """
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    surface.set_fallback_resolution(100, 100)
    ctx = cairo.Context(surface)
    ctx.scale(size/(2.0*extent), -size/(2.0*extent))
    ctx.translate(extent, -extent)

    if bg_color is not None:
        ctx.set_source_rgb(*bg_color)
        ctx.paint()

    margin = 0.1

    for (i, j) in az.cells:
        if (az.is_black(i, j) and az.tile[(i, j)] is not None):
            if az.tile[(i, j)] == 'n':
                ctx.rectangle(i - 1 + margin, j + margin,
                              2 - 2 * margin, 1 - 2 * margin)
                ctx.set_source_rgb(*N_COLOR)

            if az.tile[(i, j)] == 's':
                ctx.rectangle(i + margin, j + margin,
                              2 - 2 * margin, 1 - 2 * margin)
                ctx.set_source_rgb(*S_COLOR)

            if az.tile[(i, j)] == 'w':
                ctx.rectangle(i + margin, j + margin,
                              1 - 2 * margin, 2 - 2 * margin)
                ctx.set_source_rgb(*W_COLOR)

            if az.tile[(i, j)] == 'e':
                ctx.rectangle(i + margin, j - 1 + margin,
                              1 - 2 * margin, 2 - 2 * margin)
                ctx.set_source_rgb(*E_COLOR)

                ctx.fill()

        surface.write_to_png(filename)


def make_animation(order, size, filename):
    """Render one frame for each step in the algorithm."""
    az = aztec.AztecDiamond(0)
    for i in range(order):
        az.delete()
        draw_with_cairo(az, size, order + 1, '_tmp{:03d}.png'.format(3 * i))

        az = az.slide()
        draw_with_cairo(az, size, order + 1, '_tmp{:03d}.png'.format(3 * i + 1))

        az.create()
        draw_with_cairo(az, size, order + 1, '_tmp{:03d}.png'.format(3 * i + 2))

    command = [CONVERTER,
               '-layers', 'Optimize',
               '-delay', '15', '_tmp%03d.png[0-{}]'.format(3 * order - 2),
               '-delay', '500', '_tmp{:03d}.png'.format(3 * order - 1),
               filename]
    subprocess.check_call(command)

    # do the clean up
    for f in glob.glob('_tmp*.png'):
        os.remove(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-order', metavar='o', type=int, default=30,
                        help='order of aztec diamond')
    parser.add_argument('-size', metavar='s', type=int, default=400,
                        help='image size')
    parser.add_argument('-filename', metavar='f', default='dominoshuffling.gif',
                        help='output filename')
    args = parser.parse_args()
    make_animation(args.order, args.size, args.filename)


if __name__ == '__main__':
    main()
