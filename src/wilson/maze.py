from encoder import GIFWriter


class Maze(object):

    def __init__ (self, width, height, margin):
        '''
        width and height should both be odd numbers.
        margin is the size of the border of the maze.
        each cell in the maze has 4 possible states:
        wall(0), tree(1), path(2), filled(3).
        '''
        self.width = width
        self.height = height
        self.grid = [[0]*height for _ in range(width)]
        self.num_changes = 0
        self.frame_box = None

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
                neighbors.append((x , y-2))
            if x <= width - 3 - margin:
                neighbors.append((x+2, y))
            if y <= height - 3 - margin:
                neighbors.append((x, y+2))
            return neighbors
          
        self.graph = {v: neighborhood(v) for v in self.cells}
        self.path = []


    def get_neighbors(self, cell):
        return self.graph[cell]


    def mark_cell(self, cell, index):
        x, y = cell
        self.grid[x][y] = index
        
        # update the frame box and counter each time we change a cell.
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


    def begin_path(self, cell):
        self.path = [cell]
        self.mark_cell(cell, 2)


    def erase_loop(self, cell):
        index = self.path.index(cell)
        self.mark_path(self.path[index:], 0)
        self.mark_cell(self.path[index], 2)
        self.path = self.path[:index+1]

    
    def add_to_path(self, cell):
        self.mark_cell(cell, 2)
        self.mark_wall(self.path[-1], cell, 2)
        self.path.append(cell)



class Animation(object):

    palette = [0,   0,   0 ,   # wall color
               100, 100, 100,  # tree color
               255,  0,  255,  # path color
               150, 200, 100]  # fill color


    def __init__(self, maze, scale, speed, loop):
        '''
        scale: size of a cell in pixels.
        speed: speed of the animation.
        loop: number of loops.
        '''
        self.maze = maze
        self.speed = speed
        self.scale = scale
        self.delay = 2
        self.trans_index = 3
        self.writer = GIFWriter(maze.width * scale, maze.height * scale, Animation.palette, loop)


    def write_to_gif(self, filename):
        self.writer.save(filename)


    def get_init_table(self, **kwargs):
        wc = kwargs.get('wall_color', None)
        tc = kwargs.get('tree_color', None)
        pc = kwargs.get('path_color', None)
        fc = kwargs.get('fill_color', None)
        return {str(index): val for index, val in enumerate([wc, tc, pc, fc]) if val is not None}


    def encode_frame(self, **kwargs):
        '''
        encode current frame (but not write it to the stream).
        note the control block is not added.
        '''
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

        # clear the box and the counter
        self.maze.num_changes = 0
        self.maze.frame_box = None
        return descriptor + self.writer.LZW_encode(input_data, self.get_init_table(**kwargs))


    def paint_background(self, **kwargs):
        '''
        use current frame as background.
        the background image is static and does not need the graphics control block.
        '''
        self.writer.data = self.encode_frame(**kwargs) + self.writer.data
    

    def render_frame(self, **kwargs):
        '''
        write current frame to the stream,
        this time the graphics control block is added.
        '''
        control = self.writer.graphics_control_block(self.delay, self.trans_index)
        self.writer.data += control + self.encode_frame(**kwargs)


    def set_delay(self, delay):
        self.delay = delay


    def set_transparent(self, index):
        self.trans_index = index


    def pad_delay_frame(self, delay):
        self.writer.data += self.writer.pad_delay_frame(delay, self.trans_index)
