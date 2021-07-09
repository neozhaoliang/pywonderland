"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A Simple Random Fractal Tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import numpy as np

try:
    import cairocffi as cairo
except ImportError:
    import cairo


ITERATIONS = 16  # total number of iterations
ROOT_COLOR = np.array([0.0, 0.0, 0.0])  # root branch color
LEAF_COLOR = np.array([1.0, 1.0, 0.2])  # leaf color
TRUNK_LEN = 200  # initial length of the trunk
TRUNK_RAD = 3.0  # initial radius of the trunk
THETA = np.pi / 2  # initial angle of the branch
ANGLE = np.pi / 4.5  # angle between branches in the same level
PERTURB = 6.0  # perturb the angle a little to make the tree look random
RATIO = 0.8  # contraction factor between successive trunks
WIDTH = 600  # image width
HEIGHT = 600  # image height
ROOT = (WIDTH / 2.0, HEIGHT + 50)  # pixel position of the root


def get_color(level):
    """
    Return an interpolation of the two colors `ROOT_COLOR` and `LEAF_COLOR`.
    """
    a = float(level) / ITERATIONS
    return a * ROOT_COLOR + (1 - a) * LEAF_COLOR


def get_line_width(level):
    """Return the line width of a given level."""
    return max(1, TRUNK_RAD * level / ITERATIONS)


def fractal_tree(
    ctx,  # a cairo context to draw on
    level,  # current level in the iterations
    start,  # (x, y) coordinates of the start of this trunk
    t,  # current trunk length
    r,  # factor to contract the trunk in each iteration
    theta,  # orientation of current trunk
    angle,  # angle between branches in the same level
    perturb,  # perturb the angle
):
    if level == 0:
        return

    x0, y0 = start
    # randomize the length
    randt = np.random.random() * t
    x, y = x0 + randt * np.cos(theta), y0 - randt * np.sin(theta)

    color = get_color(level)
    ctx.move_to(x0, y0)
    ctx.line_to(x, y)
    ctx.set_line_width(get_line_width(level))
    ctx.set_source_rgb(*color)
    ctx.stroke()

    theta1 = theta + np.random.random() * (perturb / level) * angle
    theta2 = theta - np.random.random() * (perturb / level) * angle
    # recursively draw the next branches
    fractal_tree(ctx, level - 1, (x, y), t * r, r, theta1, angle, perturb)
    fractal_tree(ctx, level - 1, (x, y), t * r, r, theta2, angle, perturb)


def main():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    fractal_tree(ctx, ITERATIONS, ROOT, TRUNK_LEN, RATIO, THETA, ANGLE, PERTURB)
    surface.write_to_png("random_fractal_tree.png")


if __name__ == "__main__":
    main()
