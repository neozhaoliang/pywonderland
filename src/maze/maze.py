from lzw import *


# our animation will use 4 different colors
palette = [ 0,   0,   0 ,  # wall color
           100, 100, 100,  # tree color
           255,  0,  255,  # path color
           150, 200, 100]  # paint color

# four possible states of a cell in a maze
iswall = 0
intree = 1
inpath = 2
painted = 3

scale = 5  # size of a cell in pixels
speed = 10 # speed of the animation
margin = 2 # margin between the maze and the border of the window



class Maze(object):

    def __init__ (self, width, height):
        '''
        width, height:  size of the maze in cells.
        should both be odd numbers, though not nessesary.
        '''
        self.width = width
        self.height = height
        self.grid = [[0]*height for _ in range(width)]
        self.num_changes = 0
        self.frame_box = None
        self.stream = bytearray()
        self.setup()
        
        
    def setup(self):
        '''
        this could be put into the __init__ function, but that will be too long
        for an init function
        '''
        self.cells = []
        # to pad margin at the border just 'shrink' the maze a little.
        for y in range(margin, self.height - margin, 2):
            for x in range(margin, self.width - margin, 2):
                self.cells.append((x, y))

        def neighborhood(cell):
            x, y = cell
            neighbors = []
            if x >= 2 + margin:
                neighbors.append((x-2, y))
            if y >= 2 + margin:
                neighbors.append((x , y-2))
            if x <= self.width - 3 - margin:
                neighbors.append((x+2, y))
            if y <= self.height - 3 - margin:
                neighbors.append((x, y+2))
            return neighbors
          
        self.graph = {v: neighborhood(v) for v in self.cells}
          
      
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
    
    
    def mark_path(self, path, index):
        for cell in path:
            self.mark_cell(cell, index)
        for cellA, cellB in zip(path[1:], path[:-1]):
            self.mark_wall(cellA, cellB, index)

            
    def check_wall(self, cellA, cellB):
        '''
        check if two cells are connected
        '''
        x = (cellA[0] + cellB[0]) // 2
        y = (cellA[1] + cellB[1]) // 2
        return self.grid[x][y] == iswall

    
    def encode_frame(self, **kwargs):
        '''
        encode current frame to byte stream.
        if frame_box is None the whole screen will be encoded.
        '''
        if self.frame_box:
            left, top, right, bottom = self.frame_box
        else:
            left, top, right, bottom = 0, 0, self.width - 1, self.height - 1
            
        width = right - left + 1
        height = bottom - top + 1
        descriptor = image_descriptor(left * scale, top * scale,
                                      width * scale, height * scale)
        
        data = [0] * width * height * scale * scale
        for i in range(len(data)):
            y = i // (width * scale * scale)
            x = (i % (width * scale)) // scale
            data[i] = self.grid[x + left][y + top]

        # clear the differ box and the counter
        self.num_changes = 0
        self.frame_box = None
        return descriptor + lzw_encoder(data, **kwargs)


    def write_to_gif(self, filename):
        with open(filename, 'wb') as f:
            f.write(logical_screen_descriptor(self.width * scale, self.height * scale)
                    + global_color_table(palette)
                    + loop_control_block(loop=0)
                    + self.stream
                    + pack('B', 0x3B))


def test(size):
    maze = Maze(size, size)
    for i, j in maze.cells:
        if (i - size//2)**2 + (j - size//2)**2 < (size//2)**2:
            maze.grid[i][j] = 1
    maze.stream += maze.encode_frame(wall_color=1, tree_color=3)
    maze.write_to_gif('test.gif')

if __name__ == '__main__':
    test(100)
