"""
Bianchi Circle Packings Visualization.

This project generates and visualizes crystallographic circle packings associated
with extended Bianchi groups Bi(m) = PSL(2, O_{-m}), where O_{-m} is the ring of integers
in the imaginary quadratic field Q(√-m). The packings are constructed via
reflection of an initial cluster across a cocluster of "virtual" circles.

References:
    - https://sites.math.rutgers.edu/~alexk/crystallographic/
"""

import sympy as sp
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from mcleod import get_cluster_and_cocluster
from draw import draw_batch
from circle import Circle

# Configure matplotlib for publication-quality output
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans", "Courier"]


def compute_bend_scale(circles):
    """Compute a common scaling factor to normalize bends to (near-)integers.

    This function finds a scale factor `s` such that `bend / s` is rational
    (ideally integer) for all circles. If the bends are not rationally related
    (e.g., non-integral packings), it falls back to `s = 1`.

    Args:
        circles (List[Circle]): List of circles with symbolic bend information
            stored in `c.v_sympy[1]`.

    Returns:
        sympy.Expr: A symbolic scaling factor `s`.
    """
    # Extract non-zero symbolic bends
    bends = [sp.simplify(c.v_sympy[1]) for c in circles if c.v_sympy[1] != 0]
    if not bends:
        return sp.Integer(1)

    base = bends[0]
    ratios = []
    for b in bends:
        # First attempt: force rational approximation
        ratio = sp.nsimplify(b / base, rational=True)
        if not isinstance(ratio, sp.Rational):
            # Second attempt: general simplification
            ratio = sp.nsimplify(b / base)
            if not ratio.is_rational:
                # Bends are not rationally related → no meaningful scale
                return sp.Integer(1)
        ratios.append(ratio)

    # Compute LCM of denominators to clear fractions
    den_lcm = sp.ilcm(*[r.q for r in ratios if isinstance(r, sp.Rational)])
    return sp.simplify(base * den_lcm)


def generate_circle_packing(
    cocluster_sympy,
    init_cluster_sympy,
    depth: int,
    max_circles: int = 1000000,
    sympy_ref_count: int = 500,
):
    """Generate a circle packing by iterated reflection.

    Starting from an initial cluster of circles, reflect them across a fixed
    cocluster of "virtual" circles for a given number of depth steps. Symbolic
    computation is used for the first `sympy_ref_count` reflections to preserve
    exact arithmetic; subsequent reflections use floating-point for speed.

    Args:
        cocluster_sympy (List[sp.Matrix]): Symbolic inversive coordinates of
            virtual (mirror) circles.
        init_cluster_sympy (List[sp.Matrix]): Symbolic inversive coordinates of
            initial seed circles.
        depth (int): Number of reflection layers to generate.
        max_circles (int, optional): Upper bound on total circles to prevent
            runaway growth. Defaults to 1e6.
        sympy_ref_count (int, optional): Number of initial reflections to
            perform with exact symbolic arithmetic. Defaults to 500.

    Returns:
        Tuple[List[Circle], List[Circle]]: Generated cluster and cocluster as
            Circle objects.
    """
    # Build cocluster (mirrors) — always kept symbolic + numeric
    cocluster = [
        Circle(v_numpy=np.array(u, dtype=np.float64).ravel(), v_sympy=u)
        for u in cocluster_sympy
    ]
    # Build initial cluster
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
                # Reflect with symbolic arithmetic only for early steps
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

        if not new_frontier or len(cluster) >= max_circles:
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
    max_circles: int = 100000,
    sympy_ref_count: int = 500,
):
    # Fetch symbolic inversive coordinates for cluster and cocluster
    cl_data, co_data = get_cluster_and_cocluster(m, cluster_1based)

    fig, ax = plt.subplots(figsize=figsize)
    fig.canvas.manager.set_window_title(
        f"Bi({m}) | clusters={cluster_1based} | depth={depth}"
    )

    ax.set_aspect("equal", "box")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")

    # Generate full packing
    cluster, cocluster = generate_circle_packing(
        co_data,
        cl_data,
        depth=depth,
        max_circles=max_circles,
        sympy_ref_count=sympy_ref_count,
    )

    # Compute bend normalization scale
    circles_with_sympy = [c for c in cluster if c.v_sympy is not None]
    s_expr = compute_bend_scale(circles_with_sympy)
    print(f"Computed bend scale s = {s_expr}")
    s_float = float(sp.N(s_expr, 40))  # High-precision float for rendering

    # Prepare bend labels: symbolic if available, numeric fallback otherwise
    bend_texts = []
    for c in cluster:
        if c.v_sympy is not None:
            txt_expr = sp.simplify(c.v_sympy[1] / s_expr)
            txt = f"${sp.latex(txt_expr)}$"
        else:
            bend_val = c.v_numpy[1]
            scaled_bend = bend_val / s_float
            if abs(scaled_bend - round(scaled_bend)) < 1e-4:
                txt = f"${int(round(scaled_bend))}$"
            else:
                txt = f"${scaled_bend:.2f}$"
        bend_texts.append(txt)

    # Convert to geometric circles for drawing
    cluster_circles = [c.to_geometry() for c in cluster]
    cocluster_circles = [c.to_geometry() for c in cocluster]

    # Render
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
    # Example: Bi(7) packing
    main(
        m=5,
        cluster_1based=[3],
        depth=100,
        xlim=(-1.5, 1.5),
        ylim=(-0.1, 2.4),
        figsize=(6, 5),
        max_circles=2000000,
    )

    # Example: Bi(14) packing (rotated layout)
    main(
        m=14,
        cluster_1based=[1, 8],
        depth=50,
        xlim=(-0.1, 1.4),
        ylim=(-1.5, 1.5),
        figsize=(3, 6),
        max_circles=500000,
    )
