# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make GIF Animations of the Domino Shuffling Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script requires ImageMagick be installed on your computer.
Windows users also need to set the variable `CONVERTER` below
to be the path to your `convert.exe`.

Usage: python anim.py [-s] [-o] [-f]

Optional arguments here are the same with those in aztec.py.

:copyright (c) 2015 by Zhao Liang.
"""

import os
import glob
import subprocess
import argparse
import aztec


CONVERTER = 'convert'


def make_animation(order, size, filename):
    """Render one frame for each step in the algorithm."""
    az = aztec.AztecDiamond(0)
    for i in range(order):
        az.delete()
        az.render(size, order + 1, '_tmp{:03d}.png'.format(3 * i))

        az = az.slide()
        az.render(size, order + 1, '_tmp{:03d}.png'.format(3 * i + 1))

        az.create()
        az.render(size, order + 1, '_tmp{:03d}.png'.format(3 * i + 2))

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
