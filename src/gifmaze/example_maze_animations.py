"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make gif animations of maze algorithms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright (c) 2018 by Zhao Liang
"""
from colorsys import hls_to_rgb

import gifmaze.algorithms as algo
from gifmaze import (
    Animation,
    GIFSurface,
    Maze,
    create_animation_for_size,
    encode_maze,
    generate_text_mask,
)

width, height = 80, 40
cell_size = 4
lw = 4
margin = 6


def example1():
    """A basic maze animation example.

    Three ingredients for making an animation:

    maze: for running algorithms.
    surface: for maintaining information of the gif image.
    anim: for encoding the maze into frames.
    """
    maze, surface, anim = create_animation_for_size(
        width, height, cell_size, lw, margin
    )
    # surface: set global palette
    surface.set_palette([0, 0, 0, 255, 255, 255])
    anim.pause(100)
    # anim: encode the maze
    anim.run(algo.random_dfs, maze, speed=30, delay=5, mcl=2)
    anim.pause(500)
    anim.save("random_dfs.gif")


def example2():
    """This example shows how to use a mask image in the maze.
    """
    _, surface, anim = create_animation_for_size(
        width, height, cell_size, lw, margin
    )
    surface.set_palette([0, 0, 0, 255, 255, 255])
    mask = generate_text_mask(
        (surface.width, surface.height), "UNIX", "./resources/ubuntu.ttf", 280
    )
    maze = (
        Maze(width, height, mask=mask)
        .scale(cell_size)
        .translate((margin, margin))
        .setlinewidth(lw)
    )
    anim.pause(100)
    anim.run(algo.kruskal, maze, speed=30, delay=5, mcl=2)
    anim.pause(500)
    anim.save("kruskal.gif")


def example3():
    """
    This example shows how to insert a background image at the beginning
    of the gif file while the animation is running.
    """
    maze, surface, anim = create_animation_for_size(
        width, height, cell_size, lw, margin
    )
    surface.set_palette(
        [0, 0, 0, 255, 255, 255, 50, 50, 50, 150, 200, 100, 255, 0, 255]
    )
    anim.pause(100)
    anim.run(algo.prim, maze, speed=30, delay=5, trans_index=0, mcl=2)
    anim.pause(300)
    anim.insert_frame(encode_maze(maze, cmap={1: 2}, mcl=2))
    anim.run(algo.dfs, maze, speed=10, trans_index=0, cmap={1: 1, 2: 4}, mcl=3)
    anim.pause(500)
    anim.save("prim-dfs.gif")


def example4():
    """
    This example shows how to embed the animation into a background image.
    """
    # we create a surface from a background image
    surface = GIFSurface.from_image("./resources/bg.png")
    palette = [38, 92, 66,     # wall color, the same with the blackboard's
               200, 200, 200,  # tree color
               244, 25, 220]   # path color

    # set global color palette
    for i in range(256):
        rgb = hls_to_rgb((i / 360.0) % 1, 0.5, 1.0)
        palette += [int(round(255 * x)) for x in rgb]

    surface.set_palette(palette)
    size = (surface.width, surface.height)

    # load mask texture
    mask = generate_text_mask(size, "UST", "./resources/ubuntu.ttf", 300)
    # use the mask to create a maze
    # note we have translated and scaled the maze so that it fits the blackboard
    maze = Maze(60, 38, mask=mask).scale(3).translate((50, 35)).setlinewidth(3)
    anim = Animation(surface)
    # currently nothing has happened, we just show the background image for 1 second
    anim.pause(100, trans_index=1)
    # then we draw a rectangle on top of the blackboard region
    anim.paint(48, 32, 361, 231, 0)
    anim.pause(100)
    # there is no transparent color in the maze generating stage.
    anim.run(algo.wilson, maze, speed=50, delay=2, trans_index=None, mcl=2)
    anim.pause(300)
    cmap = {i: max(i % 256, 3) for i in range(len(maze.cells))}
    # in the maze solving stage we color the walls and trees with the transparent
    # color index 0, what would happen then? since these cells are transparent we
    # can see the underlying maze through them.
    cmap.update({0: 0, 1: 0, 2: 2})
    anim.run(algo.bfs, maze, speed=30, mcl=8, delay=5, cmap=cmap, trans_index=0)
    anim.pause(500)
    anim.save("wilson-bfs.gif")


if __name__ == "__main__":
    example1()
    example2()
    example3()
    example4()
