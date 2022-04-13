"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make gif animation of Langton's ant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reproduce the image at

    "https://en.wikipedia.org/wiki/Langton%27s_ant"

:copyright (c) 2018 by Zhao Liang
"""
from gifmaze import create_animation_for_size

ncols, nrows = 80, 80  # grid size
cell_size = 5
lw = 1
margin = 6


class Ant:

    """
    The rule:
    1. At a white square, turn 90° right, flip the color of the square,
       move forward one unit.
    2. At a black square, turn 90° left, flip the color of the square,
       move forward one unit.
    """

    DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dir = 0

    def turn(self, direction):
        if direction == "right":
            self.dir = (self.dir + 1) % 4
        elif direction == "left":
            self.dir = (self.dir + 3) % 4

        self.x = (self.x + self.DIRECTIONS[self.dir][0]) % ncols
        self.y = (self.y + self.DIRECTIONS[self.dir][1]) % nrows


def langton(maze, encode_func, speed, steps):
    count = 0
    grid = [[0] * ncols for _ in range(nrows)]
    ant = Ant(40, 30)
    for _ in range(steps):
        if grid[ant.x][ant.y] == 0:
            grid[ant.x][ant.y] = 1
            maze.mark_cell((2 * ant.x, 2 * ant.y), 2)
            ant.turn("left")
        else:
            grid[ant.x][ant.y] = 0
            maze.mark_cell((2 * ant.x, 2 * ant.y), 3)
            ant.turn("right")

        maze.mark_cell((2 * ant.x, 2 * ant.y), 4)
        count += 1

        if count % speed == 0:
            yield encode_func(maze)


maze, surface, anim = create_animation_for_size(
    ncols, nrows, cell_size, lw, margin, bg_color=1, wall_init=1
)
surface.set_palette(
    [
        255, 255, 255,  # white spaces
        0, 0, 0,        # grid line color
        0, 0, 255,      # dead cells
        0, 255, 0,      # live cells
        255, 0, 0       # current position
    ]
)
anim.show_grid(maze, bg_color=0, line_color=1)
anim.pause(100)
anim.run(langton, maze, speed=5, delay=3, steps=11500, mcl=3)
anim.pause(500)
anim.save("langton_ant.gif")
