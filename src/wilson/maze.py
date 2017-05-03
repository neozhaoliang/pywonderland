from encoder import GIFWriter


# four possible states of a cell
WALL = 0
TREE = 1
PATH = 2
FILL = 3


class Maze(object):

    '''
    This class defines the very basic structure and methods we will need for handling a maze.
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
            maintains the region that to be updated

        num_changes:
            output the frame once this number of cells are changed and reset the frame_box to None.
        '''
        self.width = width
        self.height = height
        self.grid = [[0]*height for _ in range(width)]
        self.num_changes = 0
        self.frame_box = None

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
        '''mark the space between two adjacent cells'''
        wall = ((cellA[0] + cellB[0])//2,
                (cellA[1] + cellB[1])//2)
        self.mark_cell(wall, index)


    def check_wall(self, cellA, cellB):
        '''check if two adjacent cells are connected'''
        x = (cellA[0] + cellB[0]) // 2
        y = (cellA[1] + cellB[1]) // 2
        return self.grid[x][y] == WALL


    def check_tree(self, cell):
        x, y = cell
        return self.grid[x][y] == TREE


    def mark_path(self, path, index):
        for cell in path:
            self.mark_cell(cell, index)
        for cellA, cellB in zip(path[1:], path[:-1]):
            self.mark_wall(cellA, cellB, index)



class Animation(object):

    '''
    This class is built on top of the 'Maze' class for encodig the algorithms into GIF images.
    It needs several further parameters to control the resulting image:

    1. scale: the size of the GIF image is (scale) x (size of the maze).
    2. loop: the number of loops of the GIF image.
    3. delay: the delay between two successive frames.
    4. trans_index: control which transparent color is used.
    5. init_dict: map the maze to an image (to communicate with our LZW encoder).
    6. speed: control how often a frame is rendered.
    '''

    def __init__(self, maze, scale=5, speed=30, loop=0):
        self.maze = maze
        self.writer = GIFWriter(maze.width * scale, maze.height * scale, loop)
        self.scale = scale
        self.speed = speed
        self.trans_index = 3
        self.delay = 5

        # this dict is used for communicating with our LZW encoder.
        # by modifying it we can color a maze in different ways.
        self.init_table = {str(c): c for c in range(4)}


    def set_transparent(self, index):
        self.trans_index = index


    def set_delay(self, delay):
        self.delay = delay


    def set_speed(self, speed):
        self.speed = speed


    def set_colors(self, **kwargs):
        colormap = {'wall_color': '0', 'tree_color': '1',
                    'path_color': '2', 'fill_color': '3'}
        for key, val in kwargs.items():
            self.init_table[colormap[key]] = val


    def pad_delay_frame(self, delay):
        self.writer.data += self.writer.pad_delay_frame(delay, self.trans_index)


    def refresh_frame(self):
        if self.maze.num_changes >= self.speed:
            self.write_current_frame()


    def clear(self):
        '''output (possibly) remaining changes'''
        if self.maze.num_changes > 0:
            self.write_current_frame()


    def write_current_frame(self):
        control = self.writer.graphics_control_block(self.delay, self.trans_index)
        self.writer.data += control + self.encode_frame()


    def paint_background(self, **kwargs):
        '''
        If no colors are specified then previous init_table will be used.
        This function allows you to insert current frame at the beginning of the file
        to serve as the background, it does not need the graphics control block.
        '''
        if kwargs:
            self.set_colors(**kwargs)

        self.writer.data = self.encode_frame() + self.writer.data


    def encode_frame(self):
        if self.maze.frame_box:
            left, top, right, bottom = self.maze.frame_box
        else:
            left, top, right, bottom = 0, 0, self.maze.width - 1, self.maze.height - 1

        width = right - left + 1
        height = bottom - top + 1
        descriptor = self.writer.image_descriptor(left * self.scale, top * self.scale,
                                                  width * self.scale, height * self.scale)

        input_data = [0] * width * height * self.scale * self.scale
        for i in range(len(input_data)):
            y = i // (width * self.scale * self.scale)
            x = (i % (width * self.scale)) // self.scale
            input_data[i] = self.maze.grid[x + left][y + top]

        self.maze.num_changes = 0
        self.maze.frame_box = None
        return descriptor + self.writer.LZW_encode(input_data, self.init_table)


    def write_to_gif(self, filename):
        self.writer.save(filename)
