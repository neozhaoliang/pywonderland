"""
~~~~~~~~~~~~~~~~~~~~~~~~~~
Integral Apollonian Gasket
~~~~~~~~~~~~~~~~~~~~~~~~~~

See:
    https://en.wikipedia.org/wiki/Apollonian_gasket#Integral_Apollonian_circle_packings
"""

import numpy as np
import cairo


WIDTH, HEIGHT = 600, 600
surface = cairo.SVGSurface("gasket.svg", WIDTH, HEIGHT)
ctx = cairo.Context(surface)

k1, k2, k3, k4 = -1, 2, 2, 3

des = 2 * (k1 * k1 + k2 * k2 + k3 * k3 + k4 * k4) - (k1 + k2 + k3 + k4) ** 2
assert des == 0, "Invalid Apollonian gasket"

limit = 400 * max(-k1, 1)
text_limit = 100


def draw_circle(circ):
    z, k = circ
    r = 1 / k
    z = z * r
    ctx.arc(z.real, z.imag, abs(r), 0, 2 * np.pi)
    ctx.stroke()
    # don't draw text if radius is too small or the region is unbounded
    if k < 0 or k > text_limit:
        return

    ctx.set_font_size(r)
    ks = str(k)
    xbearing, ybearing, kwidth, kheight, _, _ = ctx.text_extents(ks)
    ctx.move_to(z.real - xbearing - kwidth / 2, z.imag - ybearing - kheight / 2)
    ctx.show_text(ks)
    ctx.stroke()


def get_circle(c1, c2, c3, c4):
    """Return the other circle tangent to c2, c3, c4 except c1."""
    z1, k1 = c1
    z2, k2 = c2
    z3, k3 = c3
    z4, k4 = c4
    return 2 * (z2 + z3 + z4) - z1, 2 * (k2 + k3 + k4) - k1


def draw_branch(c1, c2, c3, c4):
    c = get_circle(c1, c2, c3, c4)
    draw_circle(c)
    if c[1] > limit:
        return
    draw_branch(c2, c, c3, c4)
    draw_branch(c3, c2, c, c4)
    draw_branch(c4, c2, c3, c)


def draw_gasket(c1, c2, c3, c4):
    draw_circle(c1)
    draw_branch(c1, c2, c3, c4)
    draw_circle(c2)
    draw_branch(c2, c3, c4, c1)
    draw_circle(c3)
    draw_branch(c3, c4, c1, c2)
    draw_circle(c4)
    draw_branch(c4, c1, c2, c3)


h = (k1 + k2 + k3 + k4) / 2
l3 = h - k3
l4 = h - k4
z1 = 0
z2 = (k1 + k2) / (k1)
z3 = (complex(l4, k1) ** 2) / ((k1 + k2) * k1)
z4 = (complex(l3, -k1) ** 2) / ((k1 + k2) * k1)

ctx.translate(WIDTH / 2, HEIGHT / 2)
ctx.scale(HEIGHT / 2 - 10, HEIGHT / 2 - 10)
ctx.set_line_width(0.003 / max(-k1, 1))
ctx.set_source_rgb(1, 1, 1)
ctx.arc(0, 0, 1, 0, 2 * np.pi)
ctx.fill()
ctx.set_source_rgb(0, 0, 0)
ctx.scale(-k1, -k1)
draw_gasket((z1, k1), (z2, k2), (z3, k3), (z4, k4))
surface.finish()
