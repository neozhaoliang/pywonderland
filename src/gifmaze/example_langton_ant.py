"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make gif animation of Langton's ant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reproduce the image at

    "https://en.wikipedia.org/wiki/Langton%27s_ant"

"""
from tqdm import tqdm
from gifmaze import PixelCanvas, GIFSurface, Animation


ncols, nrows = 80, 80  # grid size
grid = [[0 for _ in range(ncols)] for _ in range(nrows)]
directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
cell_size = 15
margin = 6
image_width = cell_size * ncols + 2 * margin
image_height = cell_size * nrows + 2 * margin


class Ant(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dir = 0

    def turn(self, direction):
        if direction == "right":
            self.dir = (self.dir + 1) % 4
        elif direction == "left":
            self.dir = (self.dir + 3) % 4

        self.x = (self.x + directions[self.dir][0]) % ncols
        self.y = (self.y + directions[self.dir][1]) % nrows


def langton(canvas, render, speed, steps):
    bar = tqdm(total=steps, desc="running Langton's ant")

    count = 0
    ant = Ant(40, 30)
    for _ in range(steps):
        if grid[ant.x][ant.y] == 0:
            grid[ant.x][ant.y] = 1
            canvas.set_pixel(ant.x, ant.y, 1)
            ant.turn("left")
        else:
            grid[ant.x][ant.y] = 0
            canvas.set_pixel(ant.x, ant.y, 0)
            ant.turn("right")

        canvas.set_pixel(ant.x, ant.y, 2)
        count += 1
        bar.update(1)

        if count % speed == 0:
            yield render(canvas)

    bar.close()


surface = GIFSurface(image_width, image_height, bg_color=0)
surface.set_palette([255, 255, 255,
                     0, 0, 0,
                     255, 0, 0,
                     0, 0, 255])
canvas = PixelCanvas(ncols, nrows).scale(cell_size).translate((margin, margin))
anim = Animation(surface)
anim.pause(100)
anim.run(langton, canvas, speed=10, delay=3, steps=11500)
anim.pause(500)
surface.save("langton_ant.gif")
surface.close()
