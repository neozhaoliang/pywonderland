"""
A few examples, you can use inkscape to convert the
output svg to png format:

    inkscape input.svg -z -d 300 -e output.png
"""
from tilings import Euclidean2D, Poincare2D


def main():
    T = Euclidean2D((3, 3, 3), (1, 1, 1))
    T.build_geometry(60)
    T.render("omnitruncated-3-3-3.svg", 1200, 960)

    T = Euclidean2D((6, 2, 3), (1, 0, 1))
    T.build_geometry(60)
    T.render("bitruncated-6-2-3.svg", 1200, 960,
             show_vertices_labels=True,
             face_colors=("#477984", "#EEAA4D", "#C03C44"))

    T = Euclidean2D((4, 2, 4), (1, 1, 1))
    T.build_geometry(60)
    T.render("omnitruncated-4-2-4.svg", 1200, 960)

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
