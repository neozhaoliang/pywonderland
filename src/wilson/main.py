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
from maze import Maze, Animation


def wilson(width, height, margin, scale, speed, loop):
    maze = Maze(width, height, margin)
    anim = Animation(maze, scale, speed, loop)

    # here we need to paint the blank background because the region that has not been
    # covered by any frame will be set to transparent by decoders.
    # comment this line and watch the result if you don't understand this.
    anim.paint_background(wall_color=0)

    # pad a one second delay
    anim.pad_delay_frame(100)

    # the root is default to be the top-left corner
    root = (margin, margin)
    # initially the tree = {root}
    tree = set([root])
    maze.mark_cell(root, 1)

    for cell in maze.cells:
        if cell not in tree:

            # start a random walk from this cell
            maze.begin_path(cell)
            current_cell = cell
            
            # while this walk has not meet the tree, move one step further.
            while current_cell not in tree:
                next_cell = random.choice(maze.get_neighbors(current_cell))                
                if next_cell in maze.path:    # thus we have found a loop, erase it!
                    maze.erase_loop(next_cell)
                else:
                    maze.add_to_path(next_cell)
                    
                current_cell = next_cell
                if maze.num_changes >= anim.speed:
                    anim.render_frame(wall_color=0, tree_color=1, path_color=2)

            # add the result path to the tree
            tree = tree.union(maze.path)
            maze.mark_path(maze.path, 1)

    # write remaining changes if there are any.
    if maze.num_changes > 0:
        anim.render_frame(wall_color=0, tree_color=1, path_color=2)

    # pad a two-seconds delay to see the maze clearly.
    anim.pad_delay_frame(200)

    
    # now we have finished Wilson algorithm's animation and you may view the
    # result now, just uncomment the following line!

    # anim.write_to_gif('wilson.gif')

    # but wait, why not add another animation? Let's solve this maze!

    # we will look for a path from the top left corner to the bottom right corner
    start = (margin, margin)
    end = (width - margin - 1, height - margin - 1)
    visited = set([start])
    stack = [(start, start)]
    parent = dict()    # use a dict to retrieve the path
    maze.mark_cell(start, 3)
    anim.set_transparent(0)
    anim.set_delay(5)

    while stack:
        current, last = stack.pop()
        parent[current] = last
        maze.mark_wall(current, last, 3)
        
        if current == end:
            break
        else:
            maze.mark_cell(current, 3)
            for next_cell in maze.get_neighbors(current):
                if (next_cell not in visited) and (not maze.check_wall(current, next_cell)):
                    stack.append((next_cell, current))
                    visited.add(next_cell)

        if maze.num_changes >= anim.speed:
            anim.render_frame(wall_color=0, tree_color=0, fill_color=3)
        
    if maze.num_changes > 0:
        anim.render_frame(wall_color=0, tree_color=0, fill_color=3)

    # retrieve the path between start and end
    path = [end]
    tmp = end
    while tmp != start:
        tmp = parent[tmp]
        path.append(tmp)

    # mark this path
    maze.mark_path(path, 2)
    anim.render_frame(wall_color=0, tree_color=0, path_color=2, fill_color=3)
    anim.pad_delay_frame(500)
    return anim


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

    args = parser.parse_args()
    
    anim = wilson(args.width, args.height, args.margin, args.scale, args.speed, args.loop)
    anim.write_to_gif('wilson_and_dfs.gif')


    
if __name__ == '__main__':
    main()  
