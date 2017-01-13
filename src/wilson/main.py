'''
Make gif animations of Wilson's uniform spanning tree algorithm and other maze-solving algorithms.

Wilson's algorithm comes from probability, it samples a random spanning tree with equal probability
among all spanning trees of a given simple, finite, connected graph. It's runs as follows:

1. choose any vertex v as the root, maintain a tree T, initially T = {v}.
2. for any vertex z that not in T, start a loop erased random walk from z, until the walk 'hits' T.
   then add the resulting path of the walk to T.
3. repeat step 2 until all vertices of the graph are in T.

for the proof of the correctness of this algorithm see Wilson's original paper:

    "Generating random spanning trees more quickly than the cover time".

The maze-solving part is a bit arbitrary and you may implement any algorithm you like, I've chosen
the depth first search algorithm for simplicity.

Example Usage: simply run

    python main.py

and enjoy the result!
'''
import argparse
import random
from encoder import GIFWriter


class Maze(object):

    '''
    this class defines the very basic structure and methods we will need.
    '''

    def __init__(self, width, height, margin):
        '''
        width, height:
            size of the maze in cells, should both be odd numbers.
        margin:
            size of the border of the maze.

        the maze is represented by a matrix with 'height' rows and 'width' columns,
        each cell in the maze has 4 possible states:

        0: this cell is a wall
        1: this cell is in the tree
        2: this cell is in the path
        3: this cell is filled (this will not be used until the path finding animation)

        initially all cells are walls.
        adjacent cells in the maze are spaced out by one cell.

        frame_box:
            maintains the region that to be updated

        num_changes:
            once this number of cells are changed, output the frame
        '''
        self.width = width
        self.height = height
        self.grid = [[0]*height for _ in range(width)]
        self.num_changes = 0
        self.frame_box = None
        self.path = []

        # shrink the maze a little to pad some margin at the border of the screen.
        self.cells = []
        for y in range(margin, height - margin, 2):
            for x in range(margin, width - margin, 2):
                self.cells.append((x, y))

        def neighborhood(cell):
            x, y = cell
            neighbors = []
            if x >= 2 + margin:
                neighbors.append((x-2, y))
            if y >= 2 + margin:
                neighbors.append((x, y-2))
            if x <= width - 3 - margin:
                neighbors.append((x+2, y))
            if y <= height - 3 - margin:
                neighbors.append((x, y+2))
            return neighbors

        self.graph = {v: neighborhood(v) for v in self.cells}

        # we will look for a path between this start and end.
        self.start = (margin, margin)
        self.end = (width - margin - 1, height - margin -1)


    def get_neighbors(self, cell):
        return self.graph[cell]


    def mark_cell(self, cell, index):
        x, y = cell
        self.grid[x][y] = index

        # update frame_box and num_changes each time we change a cell.
        self.num_changes += 1
        if self.frame_box:
            left, top, right, bottom = self.frame_box
            self.frame_box = (min(x, left), min(y, top),
                              max(x, right), max(y, bottom))
        else:
            self.frame_box = (x, y, x, y)


    def mark_wall(self, cellA, cellB, index):
        wall = ((cellA[0] + cellB[0])//2,
                (cellA[1] + cellB[1])//2)
        self.mark_cell(wall, index)


    def check_wall(self, cellA, cellB):
        x = (cellA[0] + cellB[0]) // 2
        y = (cellA[1] + cellB[1]) // 2
        return self.grid[x][y] == 0


    def mark_path(self, path, index):
        for cell in path:
            self.mark_cell(cell, index)
        for cellA, cellB in zip(path[1:], path[:-1]):
            self.mark_wall(cellA, cellB, index)



class WilsonAnimation(Maze):

    def __init__(self, width, height, margin, scale, speed, loop):
        '''
        scale: size of a cell in pixels.
        speed: speed of the animation.
        loop: number of loops.
        '''
        Maze.__init__(self, width, height, margin)
        self.writer = GIFWriter(width * scale, height * scale, loop)
        self.scale = scale
        self.speed = speed
        self.trans_index = 3

        # this table is used for communicating with our LZW encoder.
        # by modifying it we can color a maze in different ways.
        self.init_table = {str(c): c for c in range(4)}


    def __call__(self, filename):

        # here we need to paint the blank background because the region that has not been
        # covered by any frame will be set to transparent by decoders.
        # comment this line and watch the result if you don't understand this.
        self.paint_background()

        # pad a one-second delay
        self.pad_delay_frame(100)

        # in the wilson algorithm step no cells are 'filled',
        # hence it's safe to use color 3 as the transparent color.
        self.make_wison_animation(delay=2, trans_index=3,
                                  wall_color=0, tree_color=1, path_color=2)

        # pad a three-seconds delay to help to see the resulting maze clearly.
        self.pad_delay_frame(300)

        # in the dfs algorithm step the walls are unchanged throughout,
        # hence it's safe to use color 0 as the transparent color.
        self.make_dfs_animation(delay=5, trans_index=0, wall_color=0,
                                tree_color=0, path_color=2, fill_color=3)

        # pad a five-seconds delay to help to see the resulting path clearly.
        self.pad_delay_frame(500)
        self.write_to_gif(filename)


    def make_wison_animation(self, delay, trans_index, **kwargs):
        '''
        animating the Wilson algorithm.
        '''
        self.set_delay(delay)
        self.set_transparent(trans_index)
        self.set_colors(**kwargs)

        # initially the tree only contains the root.
        self.init_tree(self.start)
        for cell in self.cells:
            if cell not in self.tree:
                self.loop_erased_random_walk(cell)
        self.clear()


    def init_tree(self, root):
        self.tree = set([root])
        self.mark_cell(root, 1)


    def loop_erased_random_walk(self, cell):
        '''
        start a loop erased random walk from this cell until it hits the tree.
        '''
        self.begin_path(cell)
        current_cell = cell

        while current_cell not in self.tree:
            current_cell = self.move_one_step(current_cell)
            self.refresh_frame()

        # once the walk meets the tree, add the path to the tree.
        self.tree = self.tree.union(self.path)
        self.mark_path(self.path, 1)


    def begin_path(self, cell):
        self.path = [cell]
        self.mark_cell(cell, 2)


    def move_one_step(self, cell):
        next_cell = random.choice(self.get_neighbors(cell))

        # if next_cell is already in path, then we have found a loop in our path, erase it!
        if next_cell in self.path:
            self.erase_loop(next_cell)
        else:
            self.add_to_path(next_cell)
        return next_cell


    def erase_loop(self, cell):
        index = self.path.index(cell)
        self.mark_path(self.path[index:], 0)
        self.mark_cell(self.path[index], 2)
        self.path = self.path[:index+1]


    def add_to_path(self, cell):
        self.mark_cell(cell, 2)
        self.mark_wall(self.path[-1], cell, 2)
        self.path.append(cell)


    def make_dfs_animation(self, delay, trans_index, **kwargs):
        '''
        animating the depth first search algorithm.
        '''
        self.set_delay(delay)
        self.set_transparent(trans_index)
        self.set_colors(**kwargs)

        # despite a stack to run the dfs, we need a dict to remember each step.
        from_to = dict()
        stack = [(self.start, self.start)]
        visited = set([self.start])

        while stack:
            parent, child = stack.pop()
            from_to[parent] = child
            self.mark_cell(child, 3)
            self.mark_wall(parent, child, 3)

            if child == self.end:
                break
            else:
                for next_cell in self.get_neighbors(child):
                    if (next_cell not in visited) and (not self.check_wall(child, next_cell)):
                        stack.append((child, next_cell))
                        visited.add(next_cell)

            self.refresh_frame()
        self.clear()

        # retrieve the path
        path = [self.start]
        tmp = self.start
        while tmp != self.end:
            tmp = from_to[tmp]
            path.append(tmp)

        self.mark_path(path, 2)
        # show the path
        self.refresh_frame()


    def set_transparent(self, index):
        self.trans_index = index


    def set_delay(self, delay):
        self.delay = delay


    def set_colors(self, **kwargs):
        colormap = {'wall_color': '0', 'tree_color': '1',
                    'path_color': '2', 'fill_color': '3'}
        for key, val in kwargs.items():
            self.init_table[colormap[key]] = val


    def pad_delay_frame(self, delay):
        self.writer.data += self.writer.pad_delay_frame(delay, self.trans_index)


    def refresh_frame(self):
        if self.num_changes >= self.speed:
            self.write_current_frame()


    def clear(self):
        '''
        if there are remaining changes that has not been rendered, output them.
        '''
        if self.num_changes > 0:
            self.write_current_frame()


    def write_current_frame(self):
        control = self.writer.graphics_control_block(self.delay, self.trans_index)
        self.writer.data += control + self.encode_frame()


    def paint_background(self, **kwargs):
        '''
        if no colors are specified then previous self.init_table will be used.
        this function allows you to insert current frame at the beginning of the file
        to serve as the background, it does not need the graphics control block.
        '''
        if kwargs:
            self.set_colors(**kwargs)
        else:
            self.writer.data = self.encode_frame() + self.writer.data


    def encode_frame(self):
        '''
        encode the frame, but not write the result to the stream.
        '''
        if self.frame_box:
            left, top, right, bottom = self.frame_box
        else:
            left, top, right, bottom = 0, 0, self.width - 1, self.height - 1

        width = right - left + 1
        height = bottom - top + 1
        descriptor = self.writer.image_descriptor(left * self.scale, top * self.scale,
                                                  width * self.scale, height * self.scale)

        input_data = [0] * width * height * self.scale * self.scale
        for i in range(len(input_data)):
            y = i // (width * self.scale * self.scale)
            x = (i % (width * self.scale)) // self.scale
            input_data[i] = self.grid[x + left][y + top]

        self.num_changes = 0
        self.frame_box = None
        return descriptor + self.writer.LZW_encode(input_data, self.init_table)


    def write_to_gif(self, filename):
        self.writer.save(filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-width', metavar='w', type=int, default=101,
                        help='width of the maze')
    parser.add_argument('-height', metavar='h', type=int, default=81,
                        help='height of the maze')
    parser.add_argument('-margin', metavar='m', type=int, default=2,
                        help='border of the maze')
    parser.add_argument('-speed', type=int, default=10,
                        help='speed of the animation')
    parser.add_argument('-scale', type=int, default=5,
                        help='size of a cell in pixels')
    parser.add_argument('-loop', type=int, default=0,
                        help='number of loops of the animation, default to 0 (loop infinitely)')
    parser.add_argument('-filename', metavar='-f', type=str, default='wilson.gif',
                        help='output file name')

    args = parser.parse_args()
    WilsonAnimation(args.width, args.height, args.margin,
                    args.scale, args.speed, args.loop)(args.filename)


if __name__ == '__main__':
    main()
