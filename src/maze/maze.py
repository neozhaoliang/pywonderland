'''
This script makes GIF animations of the Wilson algorithm by directly
encoding frames into byte streams with LZW algorithm. It might be useful for the following purposes:

1. Visualize how Wilson algorithm works on a 2d grid.

2. A playground for implementing various maze solving algorithms.

3. A quick example shows how to implement a LZW encoder for GIF files.

4. Help you understand the structure of a GIF file, especially how to
combine the transparent and disposal features to make nice animations.

5. You can also extend this method to animate Conway's game of life,
Langton' ant, ... many other possibilities.

Features:

1. Pure python with built-in functions/modules, no dependencies needed.

2. Neat and small output file, just wait a few seconds to see the result!

Any suggestions are welcomed: zhao liang <mathzhaoliang@gmail.com>
'''
import random
from lzw import *


wall_color = [0, 0, 0]
tree_color = [100, 100, 100]
path_color = [255, 0, 255]
paint_color = [150, 200, 100]

iswall = wall_color_index = 0
intree = tree_color_index = 1
inpath = path_color_index = 2
painted = paint_color_index = 3

# size of cell in pixels
scale = 5
# speed of the animation
speed = 10
# margin between the maze and the border of window
# size in cells
margin = 2



class Maze(object):

    def __init__ (self, width, height):
        '''
        width, height:  size of the image in cells.
        should both be odd numbers, though works for any positive integers.
        '''
        self.width = width
        self.height = height
        self.canvas_width = width * scale
        self.canvas_height = height * scale
        self.data = [[0] * self.canvas_height for _ in range(self.canvas_width)]
        self.num_changes = 0
        self.diff_box = None

        self.cells = []
        # to pad margin at the border just 'shrink' the maze a little.
        # well, this isn't very comfortable mathematically but it does the trick in a cheap way.
        # the order that how the cells are added is irrelevant,
        # it only changes the appearance of the animation.
        for y in range(margin, height - margin, 2):
            for x in range(margin, width - margin, 2):
                self.cells.append((x, y))


    def encode_image(self, left, top, *color_indexes):
        imagedata = [self.data[x][y] for y in range(self.canvas_height) for x in range(self.canvas_width)]

        stream = lzw_encoder(imagedata, *color_indexes)
        descriptor = image_descriptor(left * scale, top * scale,
                                      self.canvas_width, self.canvas_height)
        return descriptor + stream


    def mark_cell(self, cell, index):
        x, y = cell
        for ox in range(scale):
            for oy in range(scale):
                self.data[x*scale + ox][y*scale + oy] = index


        self.num_changes += 1

        # update the differ box each time we change a cell
        if self.diff_box:
            left, top, right, bottom = self.diff_box
            self.diff_box = (min(x, left), min(y, top),
                             max(x, right), max(y, bottom))
        else:
            self.diff_box = (x, y, x, y)


    def output_frame(self, *color_indexes):
        left, top, right, bottom = self.diff_box
        width = (right - left) + 1
        height = (bottom - top) + 1
        mask = Maze(width, height)

        for y in range(top, bottom+1):
            for x in range(left, right+1):
                mask.mark_cell((x - left, y- top), self.data[x*scale][y*scale])

        # clear the differ box and the counter
        self.num_changes = 0
        self.diff_box = None
        return mask.encode_image(left, top, *color_indexes)


    def get_neighbors(self, cell):
        x, y = cell
        neighbors = []
        if x >= 2 + margin:
            neighbors.append((x-2, y))
        if y >= 2 + margin:
            neighbors.append((x, y-2))
        if x <= self.width - 3 - margin:
            neighbors.append((x+2, y))
        if y <= self.height - 3 - margin:
            neighbors.append((x, y+2))

        # return a shuffled list for randomized dfs/bfs if you like
        random.shuffle(neighbors)
        return neighbors


    def mark_wall(self, cellA, cellB, index):
        wall = ((cellA[0] + cellB[0])//2,
                (cellA[1] + cellB[1])//2)
        self.mark_cell(wall, index)


    def mark_path(self, path, index):
        for cell in path:
            self.mark_cell(cell, index)
        for cellA, cellB in zip(path[1:], path[:-1]):
            self.mark_wall(cellA, cellB, index)


    def check_wall(self, cellA, cellB):
        '''
        check if two cells are connected
        '''
        x = (cellA[0] + cellB[0])//2
        y = (cellA[1] + cellB[1])//2
        return self.data[x*scale][y*scale] == iswall


    def write_to_gif(self, stream, filename):
        screen_descriptor = logical_screen_descriptor(self.canvas_width, self.canvas_height)
        palette = global_color_table(wall_color, tree_color, path_color, paint_color)

        with open(filename, 'w') as f:
            f.write('GIF89a'
                    + screen_descriptor
                    + palette
                    + loop_control_block()
                    + stream
                    + '\x3B')



def wilson(width, height, root=(margin, margin)):
    maze = Maze(width, height)

    # we will put encoded image data into this stream
    stream = str()

    # Wilson algorithm maintains a tree, initially it's {root}
    tree = set([root])
    maze.mark_cell(root, intree)


    for cell in maze.cells:
        if cell not in tree:
            path = [cell]
            maze.mark_cell(cell, inpath)

            current_cell = cell
            # start a loop erased random walk at current_cell
            while current_cell not in tree:
                next_cell = random.choice(maze.get_neighbors(current_cell))
                if next_cell in path:
                    # so we have found a loop in the path, erase it!
                    index = path.index(next_cell)
                    maze.mark_path(path[index:], iswall)
                    maze.mark_cell(path[index], inpath)
                    path = path[:index+1]

                else:
                    # add this cell to path and continue the walk from it
                    path.append(next_cell)
                    maze.mark_cell(next_cell, inpath)
                    maze.mark_wall(current_cell, next_cell, inpath)

                current_cell = next_cell

                if maze.num_changes >= speed:
                    stream += (graphics_control_block(delay=2, trans_index=paint_color_index)
                               + maze.output_frame(wall_color_index, tree_color_index, path_color_index))


            # once the random walk hits the tree, add the path to the tree
            # and continue the loop at any new cell that is not in the tree
            tree = tree.union(path)
            maze.mark_path(path, intree)


    if maze.num_changes > 0:
        stream += (graphics_control_block(delay=2, trans_index=paint_color_index)
                   + maze.output_frame(wall_color_index, tree_color_index, path_color_index))

    # pad 1x1 pixel transparent frame for delay.
    # note we used the paint color as the transparent color.
    # this does not affect our wilson animaion since we have not
    # used the painted index so far.
    stream = (delay_frame(delay=100, trans_index=paint_color_index)
              + stream
              + delay_frame(delay=300, trans_index=paint_color_index))

    # add a background frame. since for a region that hasn't been covered by any frame yet
    # a transparent background will show though.
    stream = Maze(width, height).encode_image(0, 0, wall_color_index) + stream


    # we have finished Wilson algorithm's animation
    # and you can call the write_to_gif method to see the result now!
    # But wait, why not step further and add another animaion? Let's solve this maze!

    # you may use bread-first-search, depth-first-search, randomized-search, A-star, ...
    # you name it. I will show you how to do this with randomized depth-first-search,
    # other algorithms can be done in a similar manner and they are left to you!


    # to do a dfs search we need some data structures:
    # 1. a stack to hold cells that to be processed.
    # 2. a dict to record where to where.
    # 3. a set consists of visited cells.

    # we will start at the top-left corner and look for a way to the bottom-right corner.
    start = (margin, margin)
    end = (width - 1 - margin, height - 1 - margin)
    stack = [(root, root)]
    visited = set([start])
    where = dict()    # the dict tells us where we are from and go to where
    maze.mark_cell(start, painted)

    while stack:
        current, last = stack.pop()
        where[current] = last
        maze.mark_wall(current, last, painted)

        if current == end:
            break
        else:
            maze.mark_cell(current, painted)
            for next_cell in maze.get_neighbors(current):
                if (next_cell not in visited) and (not maze.check_wall(current, next_cell)):
                    stack.append((next_cell, current))
                    visited.add(next_cell)

        if maze.num_changes >= speed:
            stream += (graphics_control_block(delay=5, trans_index=wall_color_index)
                       + maze.output_frame(wall_color_index,
                                           wall_color_index,
                                           wall_color_index,
                                           paint_color_index))

    # It's important for you to understand how this works:
    # this time we set wall color to be the transparent color
    # and we colored wall, tree both with this transparent color,
    # so the underlying maze image we have constructed in the Wilson
    # algorithm step will show through.
    if maze.num_changes > 0:
        stream += (graphics_control_block(delay=5, trans_index=wall_color_index)
                   + maze.output_frame(wall_color_index,
                                       wall_color_index,
                                       wall_color_index,
                                       paint_color_index))

    # now add the frame that shows the path !
    # but we have to retrieve the path first:
    path = [end]
    tmp = end
    while tmp != start:
        tmp = where[tmp]
        path.append(tmp)

    maze.mark_path(path, inpath)
    stream += (graphics_control_block(delay=5, trans_index=wall_color_index)
               + maze.output_frame(wall_color_index,
                                   wall_color_index,
                                   path_color_index,
                                   paint_color_index))

    # pad a frame to show the path clearly
    stream += delay_frame(1000, trans_index=wall_color_index)
    maze.write_to_gif(stream, 'wilson.gif')


if __name__ == '__main__':
    wilson(101, 81)
