"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw Penrose P3 tiling using inflation rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import math
import cmath
import cairocffi as cairo


IMAGE_SIZE = (800, 800)
NUM_ITERATIONS = 7
PHI = (math.sqrt(5) - 1) / 2
RED = (0.697, 0.425, 0.333)
BLUE = (0, 0.4078, 0.5451)


def subdivide(triangles):
    result = []
    for color, A, B, C in triangles:
        if color == 0:
            # Subdivide red triangle
            P = A + (B - A) * PHI
            result += [(0, C, P, B), (1, P, C, A)]
        else:
            # Subdivide blue triangle
            Q = B + (A - B) * PHI
            R = B + (C - B) * PHI
            result += [(1, R, C, A), (1, Q, R, B), (0, R, Q, A)]
    return result


surface = cairo.SVGSurface("penrose.svg", IMAGE_SIZE[0], IMAGE_SIZE[1])
ctx = cairo.Context(surface)
ctx.translate(IMAGE_SIZE[0] / 2.0, IMAGE_SIZE[1] / 2.0)
wheel_radius = math.sqrt(IMAGE_SIZE[0] ** 2 + IMAGE_SIZE[1] ** 2) / math.sqrt(2)
ctx.scale(wheel_radius, wheel_radius)

# Create wheel of red triangles around the origin
triangles = []
for i in range(10):
    B = cmath.rect(1, (2*i - 1) * math.pi / 10)
    C = cmath.rect(1, (2*i + 1) * math.pi / 10)
    if i % 2 == 0:
        B, C = C, B  # Make sure to mirror every second triangle
    triangles.append((0, 0j, B, C))

for i in range(NUM_ITERATIONS):
    triangles = subdivide(triangles)

# Determine line width from size of the first triangle
color, A, B, C = triangles[0]
ctx.set_line_width(abs(B - A) / 10.0)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)

# Draw all rhombus
for color, A, B, C in triangles:
    D = B + C - A
    ctx.move_to(A.real, A.imag)
    ctx.line_to(B.real, B.imag)
    ctx.line_to(D.real, D.imag)
    ctx.line_to(C.real, C.imag)
    ctx.close_path()

    if color == 0:
        ctx.set_source_rgb(*RED)
    else:
        ctx.set_source_rgb(*BLUE)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.2, 0.2, 0.2)
    ctx.stroke()

surface.finish()
