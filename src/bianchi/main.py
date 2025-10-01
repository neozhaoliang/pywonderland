import sympy as sp
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


from mcleod import get_cluster_and_cocluster
from draw import draw_batch
from circle import Circle

mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = [
    "Helvetica",
    "Courier",
    "Arial",
    "DejaVu Sans",
]

import sympy as sp


def compute_bend_scale(circles):
    """Compute a common scale factor for the bends to make them all integers.
    This is not possible for non-integer packings, in which case we return 1.
    """
    bends = [sp.simplify(c.v_sympy[1]) for c in circles if c.v_sympy[1] != 0]
    if not bends:
        return sp.Integer(1)

    base = bends[0]
    ratios = []
    for b in bends:
        ratio = sp.nsimplify(b / base, rational=True)
        if not isinstance(ratio, sp.Rational):
            ratio = sp.nsimplify(b / base)
            if not ratio.is_rational:
                return sp.Integer(1)
        ratios.append(ratio)

    den_lcm = sp.ilcm(*[r.q for r in ratios if isinstance(r, sp.Rational)])
    return sp.simplify(base * den_lcm)


def generate_circle_packing(
    cocluster_sympy,
    init_cluster_sympy,
    depth: int,
    max_circles: int = 1000000,
    sympy_ref_count=500,
):
    cocluster = [
        Circle(v_numpy=np.array(u, dtype=np.float64).ravel(), v_sympy=u)
        for u in cocluster_sympy
    ]
    cluster = [
        Circle(v_numpy=np.array(u, dtype=np.float64).ravel(), v_sympy=u)
        for u in init_cluster_sympy
    ]
    seen = set(cluster)

    frontier = cluster.copy()
    count = 0
    for step in range(depth):
        new_frontier = []
        for virtual_circle in cocluster:
            for real_circle in frontier:
                reflected_circle = real_circle.reflect(
                    virtual_circle, do_sympy=(count < sympy_ref_count)
                )
                if reflected_circle in seen:
                    continue

                seen.add(reflected_circle)
                cluster.append(reflected_circle)
                new_frontier.append(reflected_circle)
                count += 1

            if len(cluster) >= max_circles:
                break

        if len(cluster) >= max_circles:
            break

        frontier = new_frontier
    return cluster, cocluster


def main(
    m: int,
    cluster_1based: list[int],
    depth: int,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    figsize: tuple[float, float],
    max_circles=100000,
    sympy_ref_count=500,
):
    cl_data, co_data = get_cluster_and_cocluster(m, cluster_1based)
    fig, ax = plt.subplots(figsize=figsize)
    fig.canvas.manager.set_window_title(
        f"Bi({m}) | clusters={cluster_1based} | depth={depth}"
    )

    ax.set_aspect("equal", "box")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")

    cluster, cocluster = generate_circle_packing(
        co_data,
        cl_data,
        depth=depth,
        max_circles=max_circles,
        sympy_ref_count=sympy_ref_count,
    )
    circles_with_sympy = [c for c in cluster if c.v_sympy is not None]
    s_expr = compute_bend_scale(circles_with_sympy)
    print(f"Computed bend scale s = {s_expr}")
    s_float = float(sp.N(s_expr, 40))

    bend_texts = []
    for c in cluster:
        if c.v_sympy is not None:
            txt_expr = sp.simplify(c.v_sympy[1] / s_expr)
            txt = f"${sp.latex(txt_expr)}$"
        else:
            # fallback to numeric
            bend_val = c.v_numpy[1]
            scaled_bend = bend_val / s_float
            if abs(scaled_bend - round(scaled_bend)) < 1e-4:
                txt = f"${int(round(scaled_bend))}$"
            else:
                txt = f"${scaled_bend:.2f}$"
        bend_texts.append(txt)

    cluster_circles = [c.to_geometry() for c in cluster]
    cocluster_circles = [c.to_geometry() for c in cocluster]

    draw_batch(
        ax,
        cluster_circles,
        cocluster_circles,
        xlim,
        ylim,
        bend_scale=s_float,
        bend_texts=bend_texts,
        bend_text_height_frac=0.9,
        two_digit_shrink=0.75,
    )

    plt.tight_layout()
    plt.savefig(f"Bi{m}-clusters={cluster_1based}.png", dpi=600, bbox_inches="tight")


if __name__ == "__main__":
    main(
        m=7,
        cluster_1based=[3, 4],
        depth=40,
        xlim=(-1.5, 1.5),
        ylim=(-0.1, 1.4),
        figsize=(6, 3),
    )

    main(
        m=14,
        cluster_1based=[1, 8],
        depth=50,
        xlim=(-0.1, 1.4),
        ylim=(-1.5, 1.5),
        figsize=(3, 6),
        max_circles=500000,
    )
