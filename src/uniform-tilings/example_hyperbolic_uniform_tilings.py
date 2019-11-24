import numpy as np
import cairocffi as cairo
import helpers
from tiling import PoincareTiling


def arc_to(ctx, x1, y1):
    x0, y0 = ctx.get_current_point()
    cx, cy, rad = helpers.get_circle(x0, y0, x1, y1)

    if rad is None:
        ctx.line_to(x1, y1)
        return

    A0 = np.arctan2(y0 - cy, x0 - cx)
    A1 = np.arctan2(y1 - cy, x1 - cx)

    if abs(A0 - A1) <= np.pi:
        if A0 < A1:
            ctx.arc(cx, cy, rad, A0, A1)
        else:
            ctx.arc_negative(cx, cy, rad, A0, A1)
    else:
        if A0 < A1:
            ctx.arc_negative(cx, cy, rad, A0, A1)
        else:
            ctx.arc(cx, cy, rad, A0, A1)


def draw(T, output, image_size, line_width=0.005, edge_color=0x313E4A,
         face_colors=[0x88CCEE, 0xDDCC77, 0xCC6677, 0x02CA8F]):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, image_size, image_size)
    ctx = cairo.Context(surface)
    ctx.scale(image_size / 2, -image_size / 2)
    ctx.translate(1, -1)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for (i, j), flist in T.face_indices.items():
        for face in flist:
            coords = [T.vertices_coords[k] for k in face]
            coords = [T.project(v) for v in coords]
            p = coords[0]
            ctx.move_to(*p)
            for q in coords[1:]:
                arc_to(ctx, *q)
            arc_to(ctx, *p)
            ctx.set_source_rgb(*helpers.hex_to_rgb(face_colors[(i + j) % 3]))
            ctx.fill_preserve()
            ctx.set_source_rgb(*helpers.hex_to_rgb(edge_color))
            ctx.stroke()

    ctx.arc(0, 0, 1, 0, 2*np.pi)
    ctx.set_source_rgb(0, 0, 0)
    ctx.stroke()
    surface.write_to_png(output)


if __name__ == "__main__":
    T = PoincareTiling((7, 2, 3), (-1, -1, -1))
    depth = 20
    maxcount = 1000
    T.build_geometry(depth, maxcount)
    draw(T, "723.png", 800)
    print("Coxeter group:\n{}\n".format(T.cox_mat))
    print("The automaton recognizes the shortlex language has {} states\n".format(T.G.dfa.num_states))
    T.G.dfa.draw("automaton-723.png")
    print("words up to depth {} in latex format:\n{}\n".format(depth, T.G.get_latex_words_array(T.words)))
    print("number of vertices in the tiling:\n{}\n".format(T.num_vertices))
    print("edge indices of the tiling:\n{}\n".format(T.edge_indices))
    print("face indices of the tiling:\n{}\n".format(T.face_indices))
