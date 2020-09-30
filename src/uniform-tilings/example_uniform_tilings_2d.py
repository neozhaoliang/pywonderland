"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A few 2d uniform tiling examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

you can use inkscape to convert the output svg to png format:

    inkscape input.svg -z -d 300 -e output.png
"""
from fractions import Fraction
from tiling import Euclidean2D, Poincare2D, Spherical2D, UpperHalfPlane


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

    T = Poincare2D((4, 2, 5), (-1, -1, -1))
    depth = 30
    maxcount = 20000
    T.build_geometry(depth, maxcount)
    T.render("omnitruncated-4-2-5.svg", 800,
             draw_inner_lines=True,
             show_vertices_labels=True,
             draw_labelled_edges=True)

    T = Poincare2D((2, 3, 13), (-1, 0, 0))
    depth = 40
    maxcount = 50000
    T.build_geometry(depth, maxcount)
    T.render("2-3-13.svg", 800, checker=True, draw_polygon_edges=False)

    T = Poincare2D((7, 2, 3), (-1, -1, -1))
    depth = 40
    maxcount = 50000
    T.build_geometry(depth, maxcount)
    T.render("omnitruncated-7-2-3.svg", 800, show_vertices_labels=True,
             draw_labelled_edges=True, draw_inner_lines=True,
             line_width=0.05, vertex_size=0.07,
             face_colors=("#EEAA4D", "#477984", "#C03C44"))

    T = Poincare2D((4, 3, 3), (-1, 0, 0))
    depth = 30
    maxcount = 30000
    T.build_geometry(depth, maxcount)
    T.render("regular-4-3-3.svg", 800, show_vertices_labels=True,
             draw_labelled_edges=True, draw_inner_lines=True,
             line_width=0.07, vertex_size=0.13)

    # travis can't run povray test, uncomment below to run spherical example.
    # T = Spherical2D((5, 2, 3), (1, 1, 1))
    # T.build_geometry()
    # T.render("omnitruncated-5-2-3.png", 600)

    T = UpperHalfPlane((4, 3, 3), (-1, -1, -1))
    depth = 40
    maxcount = 50000
    T.build_geometry(depth, maxcount)
    T.render("uhp-4-3-3.svg", (1600, 800),
             show_vertices_labels=True, draw_labelled_edges=True,
             draw_inner_lines=True,
             face_colors=("#477984", "#EEAA4D", "#C03C44"),
             line_width=0.05, vertex_size=0.08)


if __name__ == "__main__":
    main()
