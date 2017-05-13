import argparse
import random
from encoder import GIFWriter


# four possible states of a cell
WALL = 0
TREE = 1
PATH = 2
FILL = 3


class Maze(object):
    '''
    This class defines the structure of a maze and some methods we will need for running algorithms on it.
    '''

    def __init__(self, width, height, margin):
        '''
        width, height:
            size of the maze in cells, should both be odd numbers.

        margin:
            size of the border of the maze.

        The maze is represented by a matrix with 'height' rows and 'width' columns,
        each cell in the maze has 4 possible states:

        0: this cell is a wall
        1: this cell is in the tree
        2: this cell is in the path
        3: this cell is filled (this will not be used until the path finding animation)

        Initially all cells are walls. Adjacent cells in the maze are spaced out by one cell.

        frame_box:
            maintains the region that to be updated.

        num_changes:
            output the frame once this number of cells are changed and reset the frame_box to None.

        path:
            maintains the path in the loop erased random walk.
        '''
        self.width = width
        self.height = height
        self.grid = [[0]*height for _ in range(width)]
        self.num_changes = 0
        self.frame_box = None
        self.path = []

        # shrink the maze a little to pad some margin at the border of the window.
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
        '''
        Change the state of a cell and update 'frame_box' and 'num_changes'.
        '''
        x, y = cell
        self.grid[x][y] = index

        self.num_changes += 1

        if self.frame_box:
            left, top, right, bottom = self.frame_box
            self.frame_box = (min(x, left), min(y, top),
                              max(x, right), max(y, bottom))
        else:
            self.frame_box = (x, y, x, y)


    def mark_wall(self, cellA, cellB, index):
        '''
        Mark the space between two adjacent cells.
        '''
        wall = ((cellA[0] + cellB[0])//2,
                (cellA[1] + cellB[1])//2)
        self.mark_cell(wall, index)


    def check_wall(self, cellA, cellB):
        '''
        Check if two adjacent cells are connected.
        '''
        x = (cellA[0] + cellB[0]) // 2
        y = (cellA[1] + cellB[1]) // 2
        return self.grid[x][y] == WALL


    def mark_path(self, path, index):
        '''
        Mark the cells in a path and the spaces between them.
        '''
        for cell in path:
            self.mark_cell(cell, index)
        for cellA, cellB in zip(path[1:], path[:-1]):
            self.mark_wall(cellA, cellB, index)



class WilsonAlgoAnimation(Maze):
    '''
    Our animation contains basically two parts: run the algorithms, and write to the GIF file.
    '''

    def __init__(self, width, height, margin, scale, speed, loop):
        '''
        scale:
            each cell in the maze will be a square of (scale x scale) pixels in the image.

        speed:
            control how often a frame is rendered.

        loop:
            the number of loops of the GIF image.

        delay:
            the delay between two successive frames.

        trans_index:
            which transparent color is used.

        colormap:
            a dict that maps the maze to an image.
        '''

        Maze.__init__(self, width, height, margin)
        self.writer = GIFWriter(width * scale, height * scale, loop)
        self.scale = scale
        self.speed = speed
        self.trans_index = 3
        self.delay = 2
        self.colormap = {0: 0, 1: 1, 2: 2, 3: 3}


    def run_wilson_algorithm(self, delay, trans_index, **kwargs):
        '''
        Animating Wilson's uniform spanning tree algorithm.
        '''
        self.set_delay(delay)
        self.set_transparent(trans_index)
        self.set_colors(**kwargs)

        # initially the tree only contains the root.
        self.mark_cell(self.start, TREE)
        self.tree = set([self.start])

        # for each cell that is not in the tree,
        # start a loop erased random walk from this cell until the walk hits the tree.
        for cell in self.cells:
            if cell not in self.tree:
                self.loop_erased_random_walk(cell)

        self.clear_remaining_changes()


    def loop_erased_random_walk(self, cell):
        '''
        Start a loop erased random walk.
        '''
        self.path = [cell]
        self.mark_cell(cell, PATH)
        current_cell = cell

        while current_cell not in self.tree:
            current_cell = self.move_one_step(current_cell)
            self.refresh_frame()

        # once the walk meets the tree, add the path to the tree.
        self.mark_path(self.path, TREE)
        self.tree = self.tree.union(self.path)


    def move_one_step(self, cell):
        '''
        The most fundamental step in Wilson's algorithm:

        1. choose a random neighbor z of current cell and move to z.
        2. (i) if z is already in current path then a loop is found, erase this loop
           and continue the walk from z.
           (ii) if z is not in current path then append it to current path.
           in both cases current cell is updated to be z.
        3. repeat this procedure until z 'hits' the tree.
        '''
        next_cell = random.choice(self.get_neighbors(cell))

        if next_cell in self.path:
            self.erase_loop(next_cell)
        else:
            self.add_to_path(next_cell)

        return next_cell


    def erase_loop(self, cell):
        index = self.path.index(cell)
        # erase the loop
        self.mark_path(self.path[index:], WALL)
        # re-mark this cell
        self.mark_cell(self.path[index], PATH)
        self.path = self.path[:index+1]


    def add_to_path(self, cell):
        self.mark_cell(cell, PATH)
        self.mark_wall(self.path[-1], cell, PATH)
        self.path.append(cell)


    def run_dfs_algorithm(self, delay, trans_index, **kwargs):
        '''
        Animating the depth first search algorithm.
        '''
        self.set_delay(delay)
        self.set_transparent(trans_index)
        self.set_colors(**kwargs)

        # we use a dict to remember each step.
        from_to = dict()
        stack = [(self.start, self.start)]
        visited = set([self.start])

        while stack:
            parent, child = stack.pop()
            from_to[parent] = child
            self.mark_cell(child, FILL)
            self.mark_wall(parent, child, FILL)

            if child == self.end:
                break
            else:
                for next_cell in self.get_neighbors(child):
                    if (next_cell not in visited) and (not self.check_wall(child, next_cell)):
                        stack.append((child, next_cell))
                        visited.add(next_cell)

            self.refresh_frame()
        self.clear_remaining_changes()

        # retrieve the path
        path = [self.start]
        tmp = self.start
        while tmp != self.end:
            tmp = from_to[tmp]
            path.append(tmp)

        self.mark_path(path, PATH)
        # show the path
        self.refresh_frame()


    def set_transparent(self, index):
        self.trans_index = index


    def set_delay(self, delay):
        self.delay = delay


    def set_speed(self, speed):
        self.speed = speed


    def set_colors(self, **kwargs):
        cell_index = {'wall_color': 0, 'tree_color': 1,
                      'path_color': 2, 'fill_color': 3}
        for key, val in kwargs.items():
            self.colormap[cell_index[key]] = val


    def pad_delay_frame(self, delay):
        self.writer.data += self.writer.pad_delay_frame(delay, self.trans_index)


    def encode_frame(self):
        '''
        Encode current maze into a frame of the GIF file.
        '''
        if self.frame_box:
            left, top, right, bottom = self.frame_box
        else:
            left, top, right, bottom = 0, 0, self.width - 1, self.height - 1

        width = right - left + 1
        height = bottom - top + 1
        descriptor = self.writer.image_descriptor(left * self.scale, top * self.scale,
                                                  width * self.scale, height * self.scale)

        # flatten the pixels of the region into a 1D list.
        input_data = [0] * width * height * self.scale * self.scale
        for i in range(len(input_data)):
            y = i // (width * self.scale * self.scale)
            x = (i % (width * self.scale)) // self.scale
            value =  self.grid[x + left][y + top]
            # map the value of the cell to the color index.
            input_data[i] = self.colormap[value]

        # and don't forget to reset frame_box and num_changes.
        self.num_changes = 0
        self.frame_box = None
        return descriptor + self.writer.LZW_encode(input_data)


    def write_current_frame(self):
        control = self.writer.graphics_control_block(self.delay, self.trans_index)
        self.writer.data += control + self.encode_frame()


    def refresh_frame(self):
        if self.num_changes >= self.speed:
            self.write_current_frame()


    def clear_remaining_changes(self):
        '''
        Output (possibly) remaining changes.
        '''
        if self.num_changes > 0:
            self.write_current_frame()


    def paint_background(self, **kwargs):
        '''
        If no colors are specified then previous init_table will be used.
        This function allows you to insert current frame at the beginning of the file
        to serve as the background, it does not need the graphics control block.
        '''
        if kwargs:
            self.set_colors(**kwargs)

        self.writer.data = self.encode_frame() + self.writer.data


    def write_to_gif(self, filename):
        self.writer.save(filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-width', type=int, default=121,
                        help='width of the maze')
    parser.add_argument('-height', type=int, default=97,
                        help='height of the maze')
    parser.add_argument('-margin', type=int, default=2,
                        help='border of the maze')
    parser.add_argument('-speed', type=int, default=30,
                        help='speed of the animation')
    parser.add_argument('-scale', type=int, default=5,
                        help='size of a cell in pixels')
    parser.add_argument('-loop', type=int, default=0,
                        help='number of loops of the animation, default to 0 (loop infinitely)')
    parser.add_argument('-filename', metavar='-f', type=str, default='wilson.gif',
                        help='output file name')

    args = parser.parse_args()
    anim = WilsonAlgoAnimation(args.width, args.height, args.margin,
                    args.scale, args.speed, args.loop)

    # here we need to paint the blank background because the region that has not been
    # covered by any frame will be set to transparent by decoders.
    # comment this line and watch the result if you don't understand this.
    anim.paint_background()

    # pad one second delay, get ready!
    anim.pad_delay_frame(100)

    # in the wilson algorithm step no cells are 'filled',
    # hence it's safe to use color 3 as the transparent color.
    anim.run_wilson_algorithm(delay=2, trans_index=3,
                              wall_color=0, tree_color=1, path_color=2)

    # pad three seconds delay to help to see the resulting maze clearly.
    anim.pad_delay_frame(300)

    # fix a suitable speed for path finding animation.
    anim.set_speed(10)

    # in the dfs algorithm step the walls are unchanged throughout,
    # hence it's safe to use color 0 as the transparent color.
    anim.run_dfs_algorithm(delay=5, trans_index=0, wall_color=0,
                           tree_color=0, path_color=2, fill_color=3)

    # pad five seconds delay to help to see the resulting path clearly.
    anim.pad_delay_frame(500)

    # finally save the bytestream in 'wb' mode.
    anim.write_to_gif(args.filename)


if __name__ == '__main__':
    main()
