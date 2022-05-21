"""
This example draws the three types of Mobius transformations
that are isometries of the Poincare disk model, as well as
their actions on two orthogonal families of circles.
"""
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica"]
    }
)
import matplotlib.patches as patches
import matplotlib.cm as cm
import mobius


unit_circle = plt.Circle(
    (0, 0), 1, fc='none', ec='k', lw=2
)

fig = plt.figure(figsize=(5, 5))
ax = fig.add_axes([0, 0, 1, 1])
N = 16

# styles for the two families of circles/lines.
linestyle1 = dict(linestyle="-", color="k")
circstyle1 = dict(linestyle="-", ec="k")
linestyle2 = dict(linestyle="--", color="m")
circstyle2 = dict(linestyle="--", ec="m", fc="none")
# arrow style
style = dict(
    arrowstyle="Simple, tail_width=0.5, head_width=4, head_length=8",
    color="k"
)
fontstyle = dict(fontsize=20)


def example_elliptic():
    ax.clear()
    ax.axis([-1.1, 2, -1.5, 1.6])
    ax.axis("off")
    ax.add_patch(unit_circle)
    # the fixed point
    z = 0.5 + 0.2j
    # the elliptic transformation that rotates around z
    # another fixed point will be the inversion of z
    # about the unit circle.
    M = mobius.Mobius.elliptic(z, 2.*np.pi/N)
    # generate two orthogonal families of circles pass through z
    para_grid, orth_grid = mobius.generate_grids_elliptic(z, N)
    # get the fixed points, one of them will be z
    p1, p2 = M.get_fixed_points()

    # draw the first family
    for i, c in enumerate(reversed(para_grid)):
        col = cm.rainbow(i / N)
        cs = {**circstyle1, "fc": col}
        ls = linestyle1
        mobius.plot_cline(ax, c, ls, cs)

    # another family
    for i, c in enumerate(orth_grid):
        cs = circstyle2
        ls = {**linestyle2, "color": "m"}
        mobius.plot_cline(ax, c, ls, cs)

    if abs(p1) > 1.:
        p1, p2 = p2, p1

    # draw fixed points
    ax.plot(p1.real, p1.imag, "go", markersize=6)
    ax.plot(p2.real, p2.imag, "bo", markersize=6)

    # add labels
    ax.text(p1.real - 0.2, p1.imag - 0.15, "$p_1$", **fontstyle)
    ax.text(p2.real + 0.12, p2.imag + 0.1, "$p_2$", **fontstyle)
    ax.text(-0.35, 0, "$M$", **fontstyle)

    # draw arrow
    start = -0.45 + 0.3j
    end = M(start)
    ax.add_patch(
        patches.FancyArrowPatch(
            (start.real, start.imag), (end.real, end.imag),
            connectionstyle="arc3,rad=0.2",
            **style
        )
    )

    fig.savefig("elliptic.svg")


def example_parabolic():
    ax.clear()
    ax.axis([-1.1, 1.3, -1.1, 1.3])
    ax.axis("off")
    ax.add_patch(unit_circle)

    theta = np.pi / 3
    z = complex(np.cos(theta), np.sin(theta))
    M = mobius.Mobius.parabolic(z, 1)
    para_grid, orth_grid = mobius.generate_grids_parabolic(z, N)
    p1, p2 = M.get_fixed_points()

    for i, c in enumerate(para_grid):
        col = cm.rainbow(i / N)
        cs = {**circstyle1, "fc": col}
        ls = linestyle1
        mobius.plot_cline(ax, c, ls, cs)

    for i, c in enumerate(orth_grid):
        cs = circstyle2
        ls = linestyle2
        mobius.plot_cline(ax, c, ls, cs)

    ax.plot(p1.real, p1.imag, "go", markersize=6)

    ax.text(p1.real + 0.05, p1.imag, "$p$", **fontstyle)
    ax.text(-0.3, -0.2, "$M$", **fontstyle)

    start = -0.55 + 0.2j
    end = M(start)
    ax.add_patch(
        patches.FancyArrowPatch(
            (start.real, start.imag), (end.real, end.imag),
            connectionstyle=f"arc3,rad=0.33",
            **style
        )
    )

    fig.savefig("parabolic.svg")


def example_hyperbolic():
    ax.clear()
    ax.axis([-1.2, 1.2, -1.2, 1.2])
    ax.axis("off")
    ax.add_patch(unit_circle)

    theta = 0
    gamma = np.pi
    z = complex(np.cos(theta), np.sin(theta))
    w = complex(np.cos(gamma), np.sin(gamma))
    scale = 3
    M = mobius.Mobius.hyperbolic(w, z, scale)
    para_grid, orth_grid = mobius.generate_grids_hyperbolic(w, z, N, scale)
    p1, p2 = M.get_fixed_points()

    for i, c in enumerate(reversed(para_grid)):
        col = cm.rainbow(i / N)
        cs = {**circstyle1, "fc": 'none', "ec": col, "lw": 1.5}
        ls = {**linestyle1, "color": col, "lw": 1.5}
        mobius.plot_cline(ax, c, ls, cs)

    for i, c in enumerate(orth_grid):
        cs = {**circstyle2, "ec": "m"}
        ls = {**linestyle2, "color": "m"}
        mobius.plot_cline(ax, c, ls, cs)

    ax.plot(p1.real, p1.imag, "go", markersize=6)
    ax.plot(p2.real, p2.imag, "bo", markersize=6)

    ax.text(p1.real + 0.05, p1.imag - 0.15, "$p_1$", **fontstyle)
    ax.text(p2.real + 0.05, p2.imag - 0.15, "$p_2$", **fontstyle)
    ax.text(0., 0.6, "$M$", **fontstyle)

    start = -0.3 + 0.5j
    end = M(start)
    ax.add_patch(
        patches.FancyArrowPatch(
            (start.real, start.imag), (end.real, end.imag),
            connectionstyle=f"arc3,rad=-0.2",
            **style
        )
    )

    start = -0.3 - 0.5j
    end = M(start)
    ax.add_patch(
        patches.FancyArrowPatch(
            (start.real, start.imag), (end.real, end.imag),
            connectionstyle=f"arc3,rad=0.2",
            **style
        )
    )

    fig.savefig("hyperbolic.svg")


if __name__ == "__main__":
    example_elliptic()
    example_parabolic()
    example_hyperbolic()
