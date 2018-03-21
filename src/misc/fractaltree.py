# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A Simple Random Fractal Tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import random
import math
import cairocffi as cairo


IMAGE_WIDTH = 600
IMAGE_HEIGHT = 600
# ------ params control the apperance of the tree ----------
ITERATIONS = 17  # total number of iterations
ROOT_COLOR = (0, 0, 0)  # root branch color
LEAF_COLOR = (1.0, 1.0, 0.2)  # leaf color
TRUNK_LEN = 200  # initial length of the trunk
TRUNK_RAD = 3  # initial radius of the trunk
SCALE = 0.8  # contraction factor between successive trunks
THETA = math.pi / 2  # initial angle of the branch
ANGLE = math.pi / 4.5  # angle between branches in the same level
ROOT = (IMAGE_WIDTH/2.0, IMAGE_HEIGHT+50)  # pixel position of the root
PERTURB = 6.0  # perturb the angle a little to make the tree look random
# ----------------------------------------------------------

def get_color(level, root_color, tip_color):
    """
    Return an interpolation of the two colors `root_color` and `tip_color`.
    """
    return ((level*1.0/ITERATIONS)*(root_color[0]-tip_color[0])+tip_color[0],
            (level*1.0/ITERATIONS)*(root_color[1]-tip_color[1])+tip_color[1],
            (level*1.0/ITERATIONS)*(root_color[2]-tip_color[2])+tip_color[2])


def get_line_width(level):
    return max(1, TRUNK_RAD*level/ITERATIONS)


def fractal_tree(ctx,         # a cairo context to draw on
                 iterations,  # number of iterations
                 start,       # x,y coordinates of the start of this branch
                 t,           # current trunk length
                 r,           # factor to contract the trunk each iteration
                 theta,       # starting orientation
                 angle,       # angle between branches in the same iteration
                 perturb,     # perturb the angle
                 root_color,  # root color
                 tip_color):  # leave color
    if iterations == 0:
        return

    x0, y0 = start
    # randomize the length
    randt = random.random()*t
    x, y = x0 + randt * math.cos(theta), y0 - randt * math.sin(theta)
    # color the branch according to its position in the tree
    color = get_color(iterations, root_color, tip_color)
    # draw the branch
    ctx.move_to(x0, y0)
    ctx.line_to(x, y)
    ctx.set_line_width(get_line_width(iterations))
    ctx.set_source_rgb(*color)
    ctx.stroke()
    # recursive draw next branches
    fractal_tree(ctx, iterations-1, (x, y),  t*r, r, 
                 theta + (random.random())*(perturb/(iterations+1))*angle,
                 angle, perturb, root_color, tip_color)
    fractal_tree(ctx, iterations-1, (x, y),  t*r, r,
                 theta - (random.random())*(perturb/(iterations+1))*angle,
                 angle, perturb, root_color, tip_color)


def main(i):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, IMAGE_WIDTH, IMAGE_HEIGHT)
    ctx = cairo.Context(surface)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    fractal_tree(ctx, ITERATIONS, ROOT, TRUNK_LEN, SCALE,
                 THETA, ANGLE, PERTURB, ROOT_COLOR, LEAF_COLOR)
    surface.write_to_png("random_fractal_tree%03d.png")


if __name__ == "__main__":
    for i in range(100):
        main(i)
