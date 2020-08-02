"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Logistic Map and Mandelbrot set animation using taichi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapted from iq's shadertoy work at "https://www.shadertoy.com/view/XdSXWt"

Press `s` to save screenshot and `ESCAPE` to exit.
"""
import taichi as ti
import numpy as np


ti.init(debug=False, arch=ti.gpu)

WIDTH, HEIGHT = 800, 480
ymin, ymax = -1, 1
xmin, xmax = -WIDTH / HEIGHT, WIDTH/ HEIGHT
pixels = ti.Vector(3, dt=ti.f32, shape=(WIDTH, HEIGHT))
ox, oy = np.mgrid[xmin: xmax: WIDTH*1j, ymin: ymax: HEIGHT*1j]
grid = ti.Vector(2, dt=ti.f32, shape=(WIDTH, HEIGHT))
grid.from_numpy(np.stack((ox, oy), axis=2))


@ti.func
def log2(x):
    return ti.log(x) / ti.log(2)


@ti.func
def cadd(a, z):
    """
    add a real number `a` to a complex `z`.
    """
    return ti.Vector([a + z[0], z[1]])


@ti.func
def cmul(a, b):
    """
    Multiply two complex numbers `a` and `b`.
    """
    return ti.Vector([a[0] * b[0] - a[1] * b[1],
                      a[0] * b[1] + a[1] * b[0]])


@ti.func
def mix(x, y, a):
    """
    Mix two vectors `x` and `y` weighted by a real number `a`.
    """
    return ti.Vector([x[0] * (1.0 - a) + y[0] * a,
                      x[1] * (1.0 - a) + y[1] * a,
                      x[2] * (1.0 - a) + y[2] * a])


@ti.func
def clamp(x, a_min, a_max):
    return min(max(x, a_min), a_max)


@ti.func
def smoothstep(edge0, edge1, x):
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


@ti.func
def get_color(z, timef32):
    zoo = 0.62 + 0.38 * ti.cos(0.02 * timef32)
    coa = ti.cos(0.1 * (1.0 - zoo) * timef32)
    sia = ti.sin(0.1 * (1.0 - zoo) * timef32)
    zoo = ti.pow(zoo, 8.0)
    xy = ti.Vector([z[0] * coa - z[1] * sia,
                    z[0] * sia + z[1] * coa])
    cc = ti.Vector([1.0, 0.0]) + smoothstep(1.0, 0.5, zoo) * ti.Vector([0.24814, 0.7369]) + xy * zoo * 2.0
    col = ti.Vector([0.0, 0.0, 0.0])
    sc = ti.Vector([ti.abs(cc[0] - 1.0) - 1.0, cc[1]])
    if ti.dot(sc, sc) >= 1.0:
        co = 0.0
        w = ti.Vector([0.5, 0.0])
        for _ in range(256):
            if (ti.dot(w, w) > 1024.0):
                break
            w = cmul(cc, cmul(w, cadd(1.0, -w)))
            co += 1.0

        sco = co + 1.0 - log2(0.5 * (log2(ti.dot(cc, cc)) + log2(ti.dot(w, w))))
        col = 0.5 + 0.5 * ti.cos(3.0 + sco * 0.1 + ti.Vector([0.0, 0.5, 1.0]))
        if (co > 255.5):
            col = ti.Vector([0.0, 0.0, 0.0])

    if ti.abs(cc.x - 1.0) < 3.0:
        al = smoothstep(17.0, 12.0, timef32)
        col = clamp(col, 0.0, 1.0)
        x = 0.5
        for _ in range(200):
            x = cc[0] * (1.0 - x) * x
        for _ in range(200):
            x = cc[0] * (1.0 - x) * x
            col = col + mix(col,
                            ti.Vector([1.0, 1.0, 0.0]),
                            0.15 + 0.85 * ti.pow(clamp(ti.abs(sc.x + 1.0) *0.4, 0.0, 1.0), 4.0)) \
                            * al * 0.06 * ti.exp(-15000.0 * (cc.y - x) * (cc.y - x))

    return col

@ti.kernel
def render(t: ti.f32):
    for i, j in pixels:
        pixels[i, j] = get_color(grid[i, j], t)


def main():
    gui = ti.GUI("Logistic Map", res=(WIDTH, HEIGHT))
    paused = False
    save_screenshot = False
    ts = 0
    while True:
        while gui.get_event(ti.GUI.PRESS):
            e = gui.event
            if e.key == ti.GUI.ESCAPE:
                exit(0)
            elif e.key == "p":
                paused = not paused
            elif e.key == "s":
                save_screenshot = True

        if not paused:
            render(ts * 0.03)
            ts += 1

        img = pixels.to_numpy()
        if save_screenshot:
            ti.imwrite(img, "screenshot.png")
            save_screenshot = False
        gui.set_image(img)
        gui.show()


if __name__ == "__main__":
    main()
