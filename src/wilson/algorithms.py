# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Implementaion of several maze generation algorithms
and maze solving algorithms.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import heapq
import random
from collections import deque
from operator import itemgetter
from maze import Maze 


# ---------------------------
# maze generation algorithms.
# ---------------------------

def prim(maze, start):
    """Maze by Prim's algorithm."""
    priorityQueue = [(0, start, v) for v in maze.get_neighbors(start)]
    maze.mark_cell(start, Maze.TREE)

    while len(priorityQueue) > 0:
        _, parent, child = heapq.heappop(priorityQueue)
        if maze.in_tree(child):
            continue
        maze.mark_cell(child, Maze.TREE)
        maze.mark_wall(parent, child, Maze.TREE)
        for v in maze.get_neighbors(child):
            # assign a weight between 0-10.0 to this edge only when it's needed.
            weight = 10 * random.random()
            heapq.heappush(priorityQueue, (weight, child, v))

        maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()


def random_dfs(maze, start):
    """Maze by random depth-first search."""
    stack = [(start, v) for v in maze.get_neighbors(start)]
    maze.mark_cell(start, Maze.TREE)

    while len(stack) > 0:
        parent, child = stack.pop()
        if maze.in_tree(child):
            continue
        maze.mark_cell(child, Maze.TREE)
        maze.mark_wall(parent, child, Maze.TREE)
        neighbors = maze.get_neighbors(child)
        random.shuffle(neighbors)
        for v in neighbors:
            stack.append((child, v))

        maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()


def kruskal(maze):
    """Maze by Kruskal's algorithm."""
    parent = {v: v for v in maze.cells}
    rank = {v: 0 for v in maze.cells}
    edges = [(random.random(), u, v) for u in maze.cells \
             for v in maze.get_neighbors(u) if u < v]

    def find(v):
        """find the root of the subtree that v belongs to."""
        while parent[v] != v:
            v = parent[v]
        return v

    for _, u, v in sorted(edges, key=itemgetter(0)):
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

            maze.mark_cell(u, Maze.TREE)
            maze.mark_cell(v, Maze.TREE)
            maze.mark_wall(u, v, Maze.TREE)
            maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()


def wilson(maze, root):
    """
    Maze by Wilson's algorithm.
    The algorithm runs as follows:

    Given a finite, connected and undirected graph G:
    
    1. Choose any vertex v as the root and maintain a tree T. Initially T={v}.
    
    2. For any vertex v that is not in T, start a loop erased random walk from
       v until the walk hits T, then add the resulting path to T.

    3. Repeat step 2 until all vertices of G are in T.

    Reference:
        "Probability on Trees and Networks", by Russell Lyons and Yuval Peres.
    """
    maze.walkPath = []  # hold the path of the loop erased random walk.

    def add_to_path(cell):
        """Add a cell to the path of current random walk."""
        maze.mark_cell(cell, Maze.PATH)
        maze.mark_wall(maze.walkPath[-1], cell, Maze.PATH)
        maze.walkPath.append(cell)

    def erase_loop(cell):
        """
        When a cell is visited twice then a loop is created, erase it.
        """
        index = maze.walkPath.index(cell)
        # erase the loop
        maze.mark_path(maze.walkPath[index:], Maze.WALL)
        maze.mark_cell(maze.walkPath[index], Maze.PATH)
        maze.walkPath = maze.walkPath[:index+1]

    # the algorithm begins here.
    # initially the tree contains only the root.
    maze.mark_cell(root, Maze.TREE)

    # for each cell that is not in the tree,
    # start a loop erased random walk from this cell until the walk hits the tree.
    for cell in maze.cells:
        if not maze.in_tree(cell):
            maze.walkPath = [cell]
            maze.mark_cell(cell, Maze.PATH)
            currentCell = cell

            while not maze.in_tree(currentCell):
                nextCell = random.choice(maze.get_neighbors(currentCell))
                if maze.in_path(nextCell):  # if it's already in the path then a loop is found.
                    erase_loop(nextCell)
                elif maze.in_tree(nextCell):  # if the walk hits the tree then finish the walk.
                    add_to_path(nextCell)
                    # `add_to_path` will change the cell to `PATH` so we need to reset it.
                    maze.mark_cell(nextCell, Maze.TREE)
                else:  # continue the walk from this new cell.
                    add_to_path(nextCell)
                currentCell = nextCell

                maze.canvas.refresh_frame()

            # once the walk hits the tree then add its path to the tree.
            maze.mark_path(maze.walkPath, Maze.TREE)
            
    maze.canvas.clear_remaining_changes()


# ------------------------
# maze solving algorithms.
# ------------------------

# a helper function
def retrieve_path(cameFrom, start, end):
    """Get the path between the start and the end."""
    path = [end]
    v = end
    while v != start:
        v = cameFrom[v]
        path.append(v)
    return path


def bfs(maze, start, end):
    """Solve the maze by breadth-first search."""
    
    # a helper function
    def dist_to_color(distance):
        """
        Map the distance of a cell to the start to a color index. 
        This is because we must make sure that the assigned number of each cell
        lies between 0 and the total number of colors in the image,
        otherwise the initial dict of the encoder cannot recognize it.
        """
        return max(distance % maze.canvas.writer.num_colors, 3)

    dist = 0
    cameFrom = {start: start}
    queue = deque([(start, dist)])
    maze.mark_cell(start, dist_to_color(dist))
    visited = set([start])

    while len(queue) > 0:
        child, dist = queue.popleft()
        parent = cameFrom[child]
        maze.mark_cell(child, dist_to_color(dist))
        maze.mark_wall(parent, child, dist_to_color(dist))

        for nextCell in maze.get_neighbors(child):
            if (nextCell not in visited) and (not maze.barrier(child, nextCell)):
                cameFrom[nextCell] = child
                queue.append((nextCell, dist + 1))
                visited.add(nextCell)

        maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()

    # retrieve the path
    path = retrieve_path(cameFrom, start, end)
    maze.mark_path(path, Maze.PATH)
    # show the path
    maze.canvas.clear_remaining_changes()


def dfs(maze, start, end):
    """Solve the maze by depth-first search."""

    def dist_to_color(distance):
        return max(distance % maze.canvas.writer.num_colors, 3)

    dist = 0
    cameFrom = {start: start}  # a dict to remember each step.
    stack = [(start, dist)]
    maze.mark_cell(start, dist_to_color(dist))
    visited = set([start])
    
    while len(stack) > 0:
        child, dist = stack.pop()
        parent = cameFrom[child] 
        maze.mark_cell(child, dist_to_color(dist))
        maze.mark_wall(parent, child, dist_to_color(dist))
        for nextCell in maze.get_neighbors(child):
            if (nextCell not in visited) and (not maze.barrier(child, nextCell)):
                cameFrom[nextCell] = child
                stack.append((nextCell, dist + 1))
                visited.add(nextCell)

        maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()

    path = retrieve_path(cameFrom, start, end)
    maze.mark_path(path, Maze.PATH)
    maze.canvas.clear_remaining_changes()


def astar(maze, start, end):
    """Solve the maze by A* search."""
    weightedEdges = {(u, v): 1.0 for u in maze.cells for v in maze.get_neighbors(u)}
    priorityQueue = [(0, start)]
    cameFrom = {start: start}
    costSoFar = {start: 0}

    def manhattan(u, v):
        """The heuristic distance between two cells."""
        return abs(u[0] - v[0]) + abs(u[1] - v[1])

    while len(priorityQueue) > 0:
        _, child = heapq.heappop(priorityQueue)
        parent = cameFrom[child]
        maze.mark_cell(child, Maze.FILL)
        maze.mark_wall(parent, child, Maze.FILL)
        if child == end:
            break

        for nextCell in maze.get_neighbors(child):
            newCost = costSoFar[parent] + weightedEdges[(child, nextCell)]
            if (nextCell not in costSoFar or newCost < costSoFar[nextCell]) \
               and (not maze.barrier(nextCell, child)):
                costSoFar[nextCell] = newCost
                cameFrom[nextCell] = child
                priority = newCost + manhattan(nextCell, end)
                heapq.heappush(priorityQueue, (priority, nextCell))

        maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()

    path = retrieve_path(cameFrom, start, end)
    maze.mark_path(path, Maze.PATH)
    maze.canvas.clear_remaining_changes()
