"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Maze generation and solving algorithms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This file contains algorithms for generating and solving mazes.
Each algorithm is implemented as a generator function which runs on
a `maze` instance and calls an `encode_func` function to yield the data.
All algorithms have a similar interface:

    algo(maze, encode_func, speed, **kwargs)

Here `maze` is the Maze object that the algorithm runs on,
`encode_func` is the function that encodes the animation into frames,
`speed` controls how often `encode_func` is called (hence speed of the animation).
"""
import heapq
import random
from collections import deque
from operator import itemgetter

from tqdm import tqdm

from .gifmaze import Maze


def wilson(maze, encode_func, speed=50, root=(0, 0)):
    """
    Maze generation using Wilson's uniform spanning tree algorithm.
    """
    bar = tqdm(total=len(maze.cells) - 1, desc="Running Wilson's algorithm")

    def add_to_path(path, cell):
        """
        Add a cell to the path of current random walk.
        Note `path` is modified inside this function.
        """
        maze.mark_cell(cell, Maze.PATH)
        maze.mark_space(path[-1], cell, Maze.PATH)
        path.append(cell)

    def erase_loop(path, cell):
        """
        When a cell is visited twice then a loop is created, erase it.
        Note this function returns a new version of the path.
        """
        index = path.index(cell)
        # erase the loop
        maze.mark_path(path[index:], Maze.WALL)
        maze.mark_cell(path[index], Maze.PATH)
        return path[: index + 1]

    # initially the tree contains only the root.
    maze.mark_cell(root, Maze.TREE)

    # for each cell that is not in the tree,
    # start a loop erased random walk from this cell until the walk hits the tree.
    for cell in maze.cells:
        if not maze.in_tree(cell):
            # a list that holds the path of the loop erased random walk.
            lerw = [cell]
            maze.mark_cell(cell, Maze.PATH)
            current_cell = cell

            while not maze.in_tree(current_cell):
                next_cell = random.choice(maze.get_neighbors(current_cell))
                # if it's already in the path then a loop is found.
                if maze.in_path(next_cell):
                    lerw = erase_loop(lerw, next_cell)

                # if the walk hits the tree then finish the walk.
                elif maze.in_tree(next_cell):
                    add_to_path(lerw, next_cell)
                    # `add_to_path` will change the cell to `PATH` so we need to reset it.
                    maze.mark_cell(next_cell, Maze.TREE)

                # continue the walk from this new cell.
                else:
                    add_to_path(lerw, next_cell)

                current_cell = next_cell

                if maze.num_changes >= speed:
                    yield encode_func(maze)

            # once the walk hits the tree then add its path to the tree.
            maze.mark_path(lerw, Maze.TREE)
            bar.update(len(lerw) - 1)

    if maze.num_changes > 0:
        yield encode_func(maze)

    bar.close()


def bfs(maze, encode_func, speed=20, start=None, end=None):
    """
    Solve a maze using breadth-first search.
    The cells are marked by their distances to the starting cell plus three.
    This is because we must distinguish a 'flooded' cell from walls and tree.
    """
    if start is None:  # default start is the top left corner
        start = (0, 0)
    if end is None:  # default end is the bottom right corner
        end = (maze.width - 1, maze.height - 1)

    bar = tqdm(total=len(maze.cells) - 1, desc="Solving maze by bfs")
    init_dist = 3
    came_from = {start: start}  # remember the last cell we come from
    queue = deque([(start, init_dist)])
    maze.mark_cell(start, init_dist)
    visited = set([start])

    while len(queue) > 0:
        child, dist = queue.popleft()
        parent = came_from[child]
        maze.mark_cell(child, dist)
        maze.mark_space(parent, child, dist)
        bar.update(1)

        for next_cell in maze.get_neighbors(child):
            if (next_cell not in visited) and (not maze.barrier(child, next_cell)):
                came_from[next_cell] = child
                queue.append((next_cell, dist + 1))
                visited.add(next_cell)

        if maze.num_changes >= speed:
            yield encode_func(maze)

    if maze.num_changes > 0:
        yield encode_func(maze)

    # retrieve the path
    path = [end]
    v = end
    while v != start:
        v = came_from[v]
        path.append(v)

    maze.mark_path(path, Maze.PATH)
    # show the path
    yield encode_func(maze)

    bar.close()


def random_dfs(maze, encode_func, speed=10, start=(0, 0)):
    """Maze generation using random depth-first search.
    """
    bar = tqdm(total=len(maze.cells) - 1, desc="Running random depth first search")

    stack = [(start, v) for v in maze.get_neighbors(start)]
    maze.mark_cell(start, Maze.TREE)

    while len(stack) > 0:
        parent, child = stack.pop()
        if maze.in_tree(child):
            continue

        maze.mark_cell(child, Maze.TREE)
        maze.mark_space(parent, child, Maze.TREE)
        bar.update(1)

        neighbors = maze.get_neighbors(child)
        random.shuffle(neighbors)
        for v in neighbors:
            stack.append((child, v))

        if maze.num_changes >= speed:
            yield encode_func(maze)

    if maze.num_changes > 0:
        yield encode_func(maze)

    bar.close()


def dfs(maze, encode_func, speed=20, start=None, end=None):
    """Solve a maze using depth-first search.
    """
    if start is None:
        start = (0, 0)
    if end is None:
        end = (maze.width - 1, maze.height - 1)

    bar = tqdm(total=len(maze.cells) - 1, desc="Running dfs search.")

    came_from = {start: start}  # a dict to remember each step.
    stack = [start]
    maze.mark_cell(start, Maze.FILL)
    visited = set([start])

    while len(stack) > 0:
        child = stack.pop()
        if child == end:
            break
        parent = came_from[child]
        maze.mark_cell(child, Maze.FILL)
        maze.mark_space(parent, child, Maze.FILL)
        bar.update(1)
        for next_cell in maze.get_neighbors(child):
            if (next_cell not in visited) and (not maze.barrier(child, next_cell)):
                came_from[next_cell] = child
                stack.append(next_cell)
                visited.add(next_cell)

        if maze.num_changes >= speed:
            yield encode_func(maze)

    if maze.num_changes > 0:
        yield encode_func(maze)

    # retrieve the path
    path = [end]
    v = end
    while v != start:
        v = came_from[v]
        path.append(v)

    maze.mark_path(path, Maze.PATH)
    yield encode_func(maze)

    bar.close()


def prim(maze, encode_func, speed=30, start=(0, 0)):
    """Maze generation using Prim's algorithm.
    """
    bar = tqdm(total=len(maze.cells) - 1, desc="Running Prim's algorithm")

    queue = [(random.random(), start, v) for v in maze.get_neighbors(start)]
    maze.mark_cell(start, Maze.TREE)

    while len(queue) > 0:
        _, parent, child = heapq.heappop(queue)
        if maze.in_tree(child):
            continue

        maze.mark_cell(child, Maze.TREE)
        maze.mark_space(parent, child, Maze.TREE)
        bar.update(1)

        for v in maze.get_neighbors(child):
            # assign a weight to this edge only when it's needed.
            weight = random.random()
            heapq.heappush(queue, (weight, child, v))

        if maze.num_changes >= speed:
            yield encode_func(maze)

    if maze.num_changes > 0:
        yield encode_func(maze)

    bar.close()


def kruskal(maze, encode_func, speed=30):
    """Maze generation using Kruskal's algorithm.
    """
    bar = tqdm(total=len(maze.cells) - 1, desc="Running Kruskal's algorithm")

    parent = {v: v for v in maze.cells}
    rank = {v: 0 for v in maze.cells}
    edges = [
        (random.random(), u, v)
        for u in maze.cells
        for v in maze.get_neighbors(u)
        if u < v
    ]

    def find(v):
        """find the root of the subtree that v belongs to."""
        while parent[v] != v:
            v = parent[v]
        return v

    def union(u, v):
        root1 = find(u)
        root2 = find(v)

        if root1 != root2:
            if rank[root1] > rank[root2]:
                parent[root2] = root1

            elif rank[root1] < rank[root2]:
                parent[root1] = root2

            else:
                parent[root1] = root2
                rank[root2] += 1

    for _, u, v in sorted(edges, key=itemgetter(0)):
        if find(u) != find(v):
            union(u, v)
            maze.mark_cell(u, Maze.TREE)
            maze.mark_cell(v, Maze.TREE)
            maze.mark_space(u, v, Maze.TREE)
            bar.update(1)
            if maze.num_changes >= speed:
                yield encode_func(maze)

    if maze.num_changes > 0:
        yield encode_func(maze)

    bar.close()


def astar(maze, encode_func, speed, start=None, end=None):
    """Solving a maze by A* search.
    """
    if start is None:
        start = (0, 0)
    if end is None:
        end = (maze.width - 1, maze.height - 1)

    def manhattan(cellA, cellB):
        """
        The Manhattan distance between two cells.
        """
        xA, yA = cellA
        xB, yB = cellB
        return abs(xA - xB) + abs(yA - yB)

    def euclidean(cellA, cellB):
        """
        The Euclidean distance between two cells.
        """
        xA, yA = cellA
        xB, yB = cellB
        return ((xA - yA) * (xA - yA) + (xB - yB) * (xB - yB)) ** 0.5

    bar = tqdm(total=len(maze.cells) - 1, desc="Solving maze by A*")
    came_from = {start: start}
    visited = {start}
    queue = [(0, start)]
    heapq.heapify(queue)
    maze.mark_cell(start, Maze.FILL)
    while len(queue) > 0:
        dist, current = heapq.heappop(queue)
        if current == end:
            break

        parent = came_from[current]
        maze.mark_cell(current, Maze.FILL)
        maze.mark_space(parent, current, Maze.FILL)
        bar.update(1)

        for child in maze.get_neighbors(current):
            if (child not in visited) and (not maze.barrier(current, child)):
                came_from[child] = current
                dist = 0.2 * euclidean(child, start) + 0.8 * manhattan(child, end)
                heapq.heappush(queue, (dist, child))
                visited.add(child)

        if maze.num_changes >= speed:
            yield encode_func(maze)

    if maze.num_changes > 0:
        yield encode_func(maze)

    # retrieve the path
    path = [end]
    v = end
    while v != start:
        v = came_from[v]
        path.append(v)

    maze.mark_path(path, Maze.PATH)
    yield encode_func(maze)

    bar.close()
