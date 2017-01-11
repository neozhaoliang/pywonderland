import argparse
import random
from maze import Maze, Animation


def Wilson(width, height, margin, scale, speed, loop):
    maze = Maze(width, height, margin)
    anim = Animation(maze, scale, speed, loop)
    anim.paint_background(wall_color=0)
    anim.pad_delay_frame(100)

    root = (margin, margin)
    tree = set([root])
    maze.mark_cell(root, 1)

    for cell in maze.cells:
        if cell not in tree:
            maze.begin_path(cell)
            
            current_cell = cell
            while current_cell not in tree:
                next_cell = random.choice(maze.get_neighbors(current_cell))                
                if next_cell in maze.path:
                    maze.erase_loop(next_cell)
                else:
                    maze.add_to_path(next_cell)
                    
                current_cell = next_cell
                
                if maze.num_changes >= anim.speed:
                    anim.render_frame(wall_color=0, tree_color=1, path_color=2)

            tree = tree.union(maze.path)
            maze.mark_path(maze.path, 1)

    # write remaining changes if there are any.
    if maze.num_changes > 0:
        anim.render_frame(wall_color=0, tree_color=1, path_color=2)

    anim.pad_delay_frame(200)
    anim.write_to_gif('wilson.gif')

    
    # we havw just finished the Wilson algo animation and now let's solve this maze!
    start = root
    end = (width - 1 - margin, height - 1 - margin)
    stack = [(start, start)]
    visited = set([start])
    parent = dict()
    maze.mark_cell(start, 3)
    anim.set_transparent(0)
    
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
            anim.render_frame(wall_color=0, tree_color=0, path_color=0, fill_color=3)

    if maze.num_changes > 0:
        anim.render_frame(wall_color=0, tree_color=0, path_color=0, fill_color=3)

    path = [end]
    tmp = end
    while tmp != start:
        tmp = parent[tmp]
        path.append(tmp)

    maze.mark_path(path, 2)
    anim.render_frame(wall_color=0, tree_color=0, path_color=2, fill_color=3)

    anim.pad_delay_frame(500)
    anim.write_to_gif('wilson_solve.gif')



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
    Wilson(args.width, args.height, args.margin, args.scale, args.speed, args.loop)


if __name__ == '__main__':
    main()  
