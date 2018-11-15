"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Ammann-Beenker tiling by squares and lozenges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import math
import cmath
import cairocffi as cairo


IMAGE_SIZE = (800, 800)
NUM_ITERATIONS = 4
PI4 = math.pi / 4
SQRT2 = math.sqrt(2)
ALPHA = SQRT2 - 1
BETA = 1 - 1 / SQRT2
RED = (0.697, 0.425, 0.333)
BLUE = (0, 0.4078, 0.5451)


def subdivide(tiles):
    result = []

    for color, vertices in tiles:
        if color == 0:
            A, B, C, D = vertices

            P = A + (B - A) * ALPHA
            Pp = C + (B - C) * ALPHA
            Q = A + (D - A) * ALPHA
            Qp = C + (D - C) * ALPHA
            R = B + (Q + D - 2 * B) * BETA
            Rp = B + (Qp + D - 2 * B) * BETA

            lozUp = (0, (A, P, R, Q))
            lozDown = (0, (Rp, Pp, C, Qp))
            lozMid = (0, (D, R, B, Rp))
            sqUR = (1, (R, D, Q))
            sqUL = (1, (R, B, P))
            sqDL = (1, (Rp, B, Pp))
            sqDR = (1, (Rp, D, Qp))

            result += [lozUp, lozDown, lozMid, sqUL, sqUR, sqDL, sqDR]

        else:
            A, B, C = vertices

            P = B + (A - B) * ALPHA
            Q = B + (C - B) * BETA
            R = C + (B - C) * BETA
            S = A + (C - A) * ALPHA
            T = P + Q - B

            sqU = (1, (T, A, P))
            sqDL = (1, (T, R, Q))
            sqDR = (1, (R, C, S))
            lozU = (0, (A, T, R, S))
            lozD = (0, (T, P, B, Q))

            result += [lozU, lozD, sqU, sqDL, sqDR]

    return result


surface = cairo.SVGSurface("Ammann-Beenker.svg", IMAGE_SIZE[0], IMAGE_SIZE[1])
ctx = cairo.Context(surface)
ctx.translate(IMAGE_SIZE[0] / 2.0, IMAGE_SIZE[1] / 2.0)
wheel_radius = math.sqrt(IMAGE_SIZE[0] ** 2 + IMAGE_SIZE[1] ** 2) / SQRT2
ctx.scale(wheel_radius, wheel_radius)

A = 0j
tiles = []
for i in range(8):
    B = cmath.rect(1, i * PI4)
    D = cmath.rect(1, (i + 1) * PI4)
    C = B + D
    tiles.append((0, (A, B, C, D)))

for i in range(8):
    C = cmath.rect(1, i * PI4)
    B = (1 + math.sqrt(2)) * C
    A = cmath.rect(1, i * PI4) + cmath.rect(1, (i + 1) * PI4)
    tiles.append((1, (A, B, C)))

    A = cmath.rect(1, (i - 1) * PI4) + cmath.rect(1, i * PI4)
    tiles.append((1, (A, B, C)))

for i in range(NUM_ITERATIONS):
    tiles = subdivide(tiles)

color, vertices = tiles[0]
ctx.set_line_width(abs(vertices[1] - vertices[0]) / 10.0)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)

for shape, vertices in tiles:
    if shape == 0:
        A, B, C, D = vertices
        ctx.move_to(A.real, A.imag)
        ctx.line_to(B.real, B.imag)
        ctx.line_to(C.real, C.imag)
        ctx.line_to(D.real, D.imag)
        ctx.close_path()
        ctx.set_source_rgb(*RED)

    else:
        A, B, C = vertices
        ctx.move_to(A.real, A.imag)
        ctx.line_to(B.real, B.imag)
        ctx.line_to(C.real, C.imag)
        ctx.close_path()
        ctx.set_source_rgb(*BLUE)

    ctx.fill_preserve()
    ctx.set_source_rgb(0.2, 0.2, 0.2)
    ctx.stroke()

surface.finish()
