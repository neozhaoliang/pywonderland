"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
2D hyperbolic tilings in Poincare model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Quite dirty and quick implementation, requires hyperbolic
and drawSvg packages from https://github.com/cduck to
render the tilings into a svg file. Note I only borrowed the
drawing stuff.
"""
from tiling import PoincareTiling
import drawSvg
from hyperbolic import euclid
from hyperbolic.poincare.shapes import Polygon


def render(T, output, image_size,
           vertices_labels=True,
           draw_inner_lines=True,
           face_colors=["lightcoral", "mistyrose", "steelblue"]):
    d = drawSvg.Drawing(2.1, 2.1, origin="center")
    d.draw(euclid.shapes.Circle(0, 0, 1), fill="silver")
    for (i, j), flist in T.face_indices.items():
        for face in flist:
            coords = [T.project(v) for v in face.points]
            center = T.project(face.center)
            for k, D in enumerate(face.domain1):
                if len(D) == 2:
                    P, V = [T.project(p) for p in D]
                    poly = Polygon.fromVertices([P, V, center])
                else:
                    P1, V, P2 = [T.project(p) for p in D]
                    poly = Polygon.fromVertices([P1, V, P2, center])

                d.draw(poly, fill=face_colors[2 * (i + j) % 3])

                if draw_inner_lines:
                    d.draw(poly, fill="papayawhip", hwidth=0.02)

            for k, D in enumerate(face.domain2):
                if len(D) == 2:
                    P, V = [T.project(p) for p in D]
                    poly = Polygon.fromVertices([P, V, center])
                else:
                    P1, V, P2 = [T.project(p) for p in D]
                    poly = Polygon.fromVertices([P1, V, P2, center])

                d.draw(poly, fill=face_colors[2 * (i + j) % 3], opacity=0.3)

                if draw_inner_lines:
                    d.draw(poly, fill="papayawhip", hwidth=0.02)

            poly2 = Polygon.fromVertices(coords)
            d.draw(poly2, fill="#666", hwidth=0.05)

    if vertices_labels:
        for i in range(min(100, T.num_vertices)):
            d.draw(drawSvg.Text(str(i), 0.05, *T.project(T.vertices_coords[i]),
                                center=0.7, fill="yellow"))

    d.setRenderSize(w=image_size)
    d.saveSvg(output)


def main():
    T = PoincareTiling((3, 2, 7), (-1, 0, 0))
    depth = 40
    maxcount = 30000
    T.build_geometry(depth, maxcount)
    render(T, "237.svg", 800, vertices_labels=False, draw_inner_lines=False)

    T = PoincareTiling((4, 2, 5), (-1, -1, -1))
    depth = 30
    maxcount = 20000
    T.build_geometry(depth, maxcount)
    render(T, "omnitruncated-425.svg", 800)


if __name__ == "__main__":
    main()
