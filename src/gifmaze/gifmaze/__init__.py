from . import encoder
from .gentext import generate_text_mask
from .gifmaze import Animation, GIFSurface, Maze, encode_maze


def create_animation_for_size(width, height, cell_size,
                              linewidth, margin, **kwargs):
    """
    A helper function for quickly creating an animation.

    :param width & height: size of the maze.
    :param cell_size: size of the cells in pixels.
    :param linewidth: size of the walls between adjacent cells in pixels.
    :param margin: margin padded at the boundary of the window.
    :param kwargs: can be `cell_init`, `wall_init`, `bg_color`.
    """
    cell_init = kwargs.get("cell_init", 0)
    wall_init = kwargs.get("wall_init", 0)
    bg_color = kwargs.get("bg_color", 0)
    maze = Maze(width, height, cell_init=cell_init, wall_init=wall_init)
    maze.scale(cell_size).translate((margin, margin)).setlinewidth(linewidth)
    surface = GIFSurface(
        width * cell_size + (width - 1) * linewidth + 2 * margin,
        height * cell_size + (height - 1) * linewidth + 2 * margin,
        bg_color=bg_color,
    )
    animation = Animation(surface)
    return maze, surface, animation
