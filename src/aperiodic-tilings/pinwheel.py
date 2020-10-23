"""
~~~~~~~~~~~~~~~
Pinwheel Tiling
~~~~~~~~~~~~~~~
"""
try:
    import cairocffi as cairo
except ImportError:
    import cairo


IMAGE_SIZE = (800, 400)
NUM_ITERATIONS = 4
FACE_COLORS = [
    (0.9, 0.9, 0.5),
    (0.5, 1, 0.9),
    (0.3, 0.5, 0.8),
    (0.4, 0.7, 0.2),
    (1, 0.5, 0.25),
]
EDGE_COLOR = (0.3, 0.3, 0.3)


def subdivide(triangles):
    result = []
    for _, A, B, C in triangles:
        D = (A + B) / 2
        E = 0.6 * A + 0.4 * C
        F = 0.2 * A + 0.8 * C
        G = (F + B) / 2
        result.extend(
            [(0, A, E, D), (1, F, E, D), (2, D, G, F), (3, D, G, B), (4, B, F, C)]
        )
    return result


surface = cairo.SVGSurface("pinwheel.svg", IMAGE_SIZE[0], IMAGE_SIZE[1])
ctx = cairo.Context(surface)
ctx.scale(IMAGE_SIZE[0] / 2.0, -IMAGE_SIZE[1])
ctx.translate(0, -1)

triangles = [(0, 0, 2, 2 + 1j), (0, 2 + 1j, 1j, 0)]
tiles = []

for i in range(NUM_ITERATIONS):
    tiles.append(triangles)
    triangles = subdivide(triangles)

color, A, B, C = triangles[0]
lw = abs(B - A) / 20.0
ctx.set_line_width(lw)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)

for color, A, B, C in triangles:
    ctx.move_to(A.real, A.imag)
    ctx.line_to(B.real, B.imag)
    ctx.line_to(C.real, C.imag)
    ctx.close_path()

    ctx.set_source_rgb(*FACE_COLORS[color])
    ctx.fill_preserve()
    ctx.set_source_rgb(*EDGE_COLOR)
    ctx.stroke()

for k, triangles in enumerate(tiles):
    color, A, B, C = triangles[0]
    ctx.set_line_width(lw * 2 * (k + 1) / NUM_ITERATIONS)

    for color, A, B, C in triangles:
        ctx.move_to(A.real, A.imag)
        ctx.line_to(B.real, B.imag)
        ctx.line_to(C.real, C.imag)
        ctx.close_path()

        ctx.set_source_rgb(*EDGE_COLOR)
        ctx.stroke()

surface.finish()
