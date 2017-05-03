import random
from maze import *



def Prim_and_DFS(width, height, margin, scale, speed, loop):
    maze = Maze(width, height, margin)
    canvas = Animation(maze, scale, speed, loop)
    canvas.paint_background()
    canvas.pad_delay_frame(200)

    # cells that are already in the tree
    tree = set([maze.start])
    maze.mark_cell(maze.start, TREE)

    # cells that are not in the tree
    remaining = set(maze.cells) - tree

    # maintain the set edges that connect the explored cells (tree)
    # and the unexplored cells (remaining).
    frontier = set([(maze.start, v) for v in maze.get_neighbors(maze.start)])

    while remaining:
        connection, = random.sample(frontier, 1)
        frontier.remove(connection)
        explored, unexplored = connection
        maze.mark_cell(unexplored, TREE)
        maze.mark_wall(explored, unexplored, TREE)
        # update the tree and the remaining
        tree.add(unexplored)
        remaining.remove(unexplored)

        # we also update the frontier set.
        # note the function discard() does raise KeyError if the key does not exist.
        for v in tree:
            frontier.discard((v, unexplored))

        for v in maze.get_neighbors(unexplored):
            if v not in tree:
                frontier.add((unexplored, v))

        canvas.refresh_frame()

    canvas.clear()
    canvas.pad_delay_frame(300)

    canvas.set_speed(10)
    canvas.set_transparent(0)

    from_to = dict()
    visited = set([maze.start])
    stack = [(maze.start, maze.start)]
    while stack:
        parent, child = stack.pop()
        from_to[parent] = child
        maze.mark_cell(child, FILL)
        maze.mark_wall(parent, child, FILL)

        if child == maze.end:
            break
        else:
            for next_cell in maze.get_neighbors(child):
                if (next_cell not in visited) and (not maze.check_wall(child, next_cell)):
                    stack.append((child, next_cell))
                    visited.add(next_cell)

        canvas.refresh_frame()
    canvas.clear()

    path = [maze.start]
    tmp = maze.start
    while tmp != maze.end:
        tmp = from_to[tmp]
        path.append(tmp)

    maze.mark_path(path, PATH)
    canvas.refresh_frame()
    canvas.pad_delay_frame(500)
    canvas.write_to_gif('prim_and_dfs.gif')


Prim_and_DFS(width=101, height=81, margin=2,
     scale=5, speed=20, loop=0)
