import subprocess
import os
from tilings import Poincare2D


def main():
    T = Poincare2D((3, 2, 7), (-1, 0, 0))
    depth = 40
    maxcount = 30000
    T.build_geometry(depth, maxcount)
    T.render("3-2-7.svg", 800)

    T = Poincare2D((4, 2, 5), (-1, -1, -1))
    depth = 30
    maxcount = 20000
    T.build_geometry(depth, maxcount)
    T.render("omnitruncated-4-2-5.svg", 800, draw_inner_lines=True,
             show_vertices_labels=True)

    T = Poincare2D((2, 3, 13), (-1, 0, 0))
    depth = 40
    maxcount = 50000
    T.build_geometry(depth, maxcount)
    T.render("2-3-13.svg", 800, checker=True, draw_polygon_edges=False)

    T = Poincare2D((3, 4, 3), (-1, 0, 0))
    depth = 40
    maxcount = 30000
    T.build_geometry(depth, maxcount)
    T.render("3-4-3.svg", 800, checker=True, checker_colors=("white", "black"),
             draw_polygon_edges=False)


if __name__ == "__main__":
    main()
