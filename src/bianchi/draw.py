import re
from matplotlib.collections import EllipseCollection, LineCollection
import numpy as np


def add_circles(ax, circles, edgecolor, lws, linestyle):
    if not circles:
        return
    centers = np.array([(x, y) for (x, y, r) in circles])
    widths = np.array([2.0 * r for (_, _, r) in circles])
    coll = EllipseCollection(
        widths,
        widths,
        np.zeros_like(widths),
        units="xy",
        offsets=centers,
        transOffset=ax.transData,
        facecolors="none",
        edgecolors=edgecolor,
        linewidths=np.array(lws),
        linestyles=linestyle,
    )
    ax.add_collection(coll)


def add_lines(ax, segs, color, lw):
    if not segs:
        return
    ax.add_collection(LineCollection(segs, colors=color, linewidths=lw))


def visible_len_from_mathtext(s: str) -> int:
    t = s.strip()
    if t.startswith("$") and t.endswith("$"):
        t = t[1:-1]
    t = re.sub(r"\\[A-Za-z]+", "", t)
    t = t.replace("{", "").replace("}", "").replace("^", "").replace("_", "")
    return max(1, len(t))


def draw_batch(
    ax,
    cluster_circles,
    cocluster_circles,
    xlim,
    ylim,
    rlabel_min=0.01,
    bend_scale=1.0,
    bend_texts=None,
    lw_min=0.2,
    lw_max=3.0,
    label_bend=True,
    bend_text_height_frac=0.9,
    two_digit_shrink=0.7,
):
    fig = ax.figure
    mirrors, real_circles = [], []
    mirror_lws, real_lws = [], []
    segs_mirror, segs_real, texts = [], [], []

    def data_dy_to_points(dy: float) -> float:
        y0 = ax.transData.transform((0.0, 0.0))[1]
        y1 = ax.transData.transform((0.0, dy))[1]
        return abs(y1 - y0) * 72.0 / fig.dpi

    for c in cocluster_circles:
        if c[0] == "circle":
            _, cx, cy, bend = c
            # matplotlib is very slow for large circles, so skip them
            if abs(bend) < 1e-5:
                continue
            r = 1.0 / abs(bend)
            lw = 2.0
            mirrors.append((cx, cy, r))
            mirror_lws.append(lw)
        else:
            _, Px, Py, vx, vy = c
            t = 1e3
            seg = ((Px - t * vx, Py - t * vy), (Px + t * vx, Py + t * vy))
            segs_mirror.append(seg)

    for idx, c in enumerate(cluster_circles):
        if c[0] == "circle":
            _, cx, cy, bend = c
            # matplotlib is very slow for large circles, so skip them
            if abs(bend) < 1e-5:
                continue
            r = 1.0 / abs(bend)
            lw = np.clip(r, lw_min, lw_max)
            real_circles.append((cx, cy, r))
            real_lws.append(lw)

            if (
                label_bend
                and (r >= rlabel_min)
                and (xlim[0] <= cx <= xlim[1])
                and (ylim[0] <= cy <= ylim[1])
            ):
                if bend_texts is not None and idx < len(bend_texts):
                    txt = bend_texts[idx]
                else:
                    val = bend / float(bend_scale)
                    if abs(val - round(val)) < 1e-4:
                        txt = f"${int(round(val))}$"
                    else:
                        txt = f"${val:.2f}$"

                base_h = bend_text_height_frac * (2.0 * r)
                vis_len = visible_len_from_mathtext(txt)
                shrink = two_digit_shrink**vis_len
                fs_pts = max(1.0, data_dy_to_points(base_h * shrink))
                texts.append((cx, cy, txt, fs_pts, "black"))
        else:
            _, Px, Py, vx, vy = c
            t = 1e3
            seg = ((Px - t * vx, Py - t * vy), (Px + t * vx, Py + t * vy))
            segs_real.append(seg)

    add_circles(ax, mirrors, "red", mirror_lws, "-")
    add_circles(ax, real_circles, "black", real_lws, "-")
    add_lines(ax, segs_mirror, "red", 2.0)
    add_lines(ax, segs_real, "black", 1.5)

    for x, y, txt, fs_pts, col in texts:
        ax.text(
            x,
            y,
            txt,
            ha="center",
            va="center",
            fontsize=fs_pts,
            color=col,
            usetex=False,
        )
