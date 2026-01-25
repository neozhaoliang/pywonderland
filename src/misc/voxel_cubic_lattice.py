from dataclasses import dataclass
import numba as nb
import numpy as np
import svgwrite


# ---------------------------- Config ----------------------------


@dataclass(frozen=True, slots=True)
class Config:
    out_file: str = "cubic_lattice_voxel.svg"
    svg_size: tuple[str, str] = ("1000px", "1000px")
    viewbox: tuple[float, float, float, float] = (-120, -120, 240, 240)

    max_steps: int = 2000
    focal: float = 0.4
    super_sampling: int = 2

    barrel: bool = True
    barrel_b: float = -0.12
    barrel_scale: float = 1.1

    hatch_spacing: float = 0.6
    hatch_angle_deg: float = -60.0
    hatch_stroke: float = 0.25

    edge_stroke: float = 0.35


# ---------------------------- Utils ----------------------------


def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v if n < 1e-12 else v / n


def make_camera(
    origin: np.ndarray, target: np.ndarray, roll: float = 0.0
) -> np.ndarray:
    """Camera->World matrix (columns: right/up/forward, last: origin)."""
    cw = normalize(target - origin)
    cp = np.array([np.sin(roll), np.cos(roll), 0.0], np.float64)
    cu = normalize(np.cross(cw, cp))
    cv = np.cross(cu, cw)
    m = np.eye(4, dtype=np.float64)
    m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = cu, cv, cw, origin
    return m


def make_rays(viewbox, ss: int, focal: float, R: np.ndarray) -> np.ndarray:
    """Return world-space ray directions for all (super-sampled) pixels."""
    _, _, w, h = viewbox
    W, H = int(round(w)) * ss, int(round(h)) * ss

    yy, xx = np.ogrid[(H - 0.5) : 0.5 : H * 1j, 0.5 : (W - 0.5) : W * 1j]
    px = (2.0 * xx - W) / H
    py = (2.0 * yy - H) / H
    px, py = np.broadcast_arrays(px, py)

    rd = np.stack([px, py, np.full_like(px, focal)], axis=-1).astype(np.float64)
    rd /= np.linalg.norm(rd, axis=-1, keepdims=True)
    return rd.reshape(-1, 3) @ R.T


def project_faces(pos, nor, world2cam, focal: float, viewbox):
    """Project each hit face into screen space: (M,4,2)."""
    vb_x, vb_y, vb_w, vb_h = viewbox
    cx, cy = vb_x + 0.5 * vb_w, vb_y + 0.5 * vb_h
    view_scale = 0.5 * vb_h

    center = pos + 0.5
    face_c = center + 0.5 * nor

    b = nor[:, [1, 2, 0]]
    t = np.cross(nor, b)
    corners = (np.stack([-t - b, t - b, t + b, -t + b], axis=1) * 0.5).astype(
        np.float64
    )
    verts = face_c[:, None, :] + corners

    A, t0 = world2cam[:3, :3], world2cam[:3, 3]
    cp = verts @ A.T + t0
    s = focal / cp[..., 2]
    x = cp[..., 0] * s * view_scale + cx
    y = -cp[..., 1] * s * view_scale + cy
    return np.stack([x, y], axis=-1)


# ---------------------------- Numba Kernels ----------------------------


@nb.njit(cache=True)
def is_voxel(cell: np.ndarray) -> bool:
    m = cell % 15
    edge = (m[0] == 0) + (m[1] == 0) + (m[2] == 0) >= 2
    box3x3 = np.all((m < 2) | (m > 13))
    return edge or box3x3


@nb.njit(cache=True)
def cast_ray_dda(ro, rd, max_steps, out_pos, out_nor) -> bool:
    cell = np.floor(ro).astype(np.int32)
    inv = np.where(np.abs(rd) > 1e-16, 1.0 / rd, 1e32)
    step = np.where(inv >= 0.0, 1, -1).astype(np.int32)
    ra = np.abs(inv)
    ds = (cell - ro + 0.5 + 0.5 * step) * inv

    for _ in range(max_steps):
        axis = np.argmin(ds)
        ds[axis] += ra[axis]
        cell[axis] += step[axis]
        if is_voxel(cell):
            out_pos[:] = cell
            out_nor[:] = 0
            out_nor[axis] = -step[axis]
            return True
    return False


@nb.njit(cache=True, parallel=True, fastmath=True)
def raycast_pixels(origin, rds, max_steps):
    N = rds.shape[0]
    pos = np.empty((N, 3), np.int32)
    nor = np.empty((N, 3), np.int8)
    dist = np.empty(N, np.float64)
    hit = np.zeros(N, np.bool_)

    for i in nb.prange(N):
        ok = cast_ray_dda(origin, rds[i], max_steps, pos[i], nor[i])
        hit[i] = ok
        if ok:
            dist[i] = np.linalg.norm(pos[i] - origin)
        else:
            pos[i] = (-1, 0, 0)
            nor[i] = (0, 0, 0)
            dist[i] = 0.0
    return pos, nor, dist, hit


@nb.njit(cache=True)
def visible_edges(pos, nor):
    """For each face, 4 booleans: whether to draw each boundary edge."""
    M = pos.shape[0]
    edges = np.empty((M, 4), np.uint8)
    for i in range(M):
        n = nor[i]
        b = np.array([n[1], n[2], n[0]], np.int32)
        t = np.array(
            [
                n[1] * b[2] - n[2] * b[1],
                n[2] * b[0] - n[0] * b[2],
                n[0] * b[1] - n[1] * b[0],
            ],
            np.int32,
        )
        offsets = np.stack((-b, t, b, -t), axis=0)
        p1s = pos[i] + offsets
        p2s = p1s + n
        for e in range(4):
            edges[i, e] = (not is_voxel(p1s[e])) or is_voxel(p2s[e])
    return edges


# ---------------------------- SVG Path Helpers ----------------------------


def fmt(v: float) -> str:
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    if s.startswith("0."):
        s = s[1:]
    elif s.startswith("-0."):
        s = "-" + s[2:]
    return s or "0"


def barrel_xy(p: np.ndarray, cfg: Config) -> np.ndarray:
    if not cfg.barrel:
        return p
    r2 = float(p[0] * p[0] + p[1] * p[1])
    s = (1.0 + r2 * cfg.barrel_b / 1e4) * cfg.barrel_scale
    return p * s


def quad_to(p0: np.ndarray, p1: np.ndarray, cfg: Config):
    """Return (q1, ctrl) in transformed space; ctrl=None means use line."""
    if not cfg.barrel:
        return p1, None
    q0 = barrel_xy(p0, cfg)
    q1 = barrel_xy(p1, cfg)
    qm = barrel_xy((p0 + p1) * 0.5, cfg)
    ctrl = 2.0 * qm - 0.5 * (q0 + q1)
    return q1, ctrl


def path_closed_quad(quad_xy: np.ndarray, cfg: Config) -> str:
    if quad_xy.size == 0:
        return ""
    p0 = quad_xy[0]
    q0 = barrel_xy(p0, cfg)
    parts = [f"M{fmt(q0[0])},{fmt(q0[1])}"]
    for i in range(4):
        a, b = quad_xy[i], quad_xy[(i + 1) & 3]
        qb, ctrl = quad_to(a, b, cfg)
        if ctrl is None:
            parts.append(f"L{fmt(qb[0])},{fmt(qb[1])}")
        else:
            parts.append(f"Q{fmt(ctrl[0])},{fmt(ctrl[1])} {fmt(qb[0])},{fmt(qb[1])}")
    parts.append("Z")
    return "".join(parts)


def path_segments(segments: list[tuple[np.ndarray, np.ndarray]], cfg: Config) -> str:
    parts = []
    for a, b in segments:
        qa = barrel_xy(a, cfg)
        qb, ctrl = quad_to(a, b, cfg)
        parts.append(f"M{fmt(qa[0])},{fmt(qa[1])}")
        if ctrl is None:
            parts.append(f"L{fmt(qb[0])},{fmt(qb[1])}")
        else:
            parts.append(f"Q{fmt(ctrl[0])},{fmt(ctrl[1])} {fmt(qb[0])},{fmt(qb[1])}")
    return "".join(parts)


def add_defs(dwg: svgwrite.Drawing, cfg: Config):
    s = cfg.hatch_spacing
    pat = dwg.pattern(
        id="h",
        insert=(0, 0),
        size=(s, s),
        patternUnits="userSpaceOnUse",
        patternTransform=f"rotate({cfg.hatch_angle_deg})",
    )
    pat.add(dwg.rect(insert=(0, 0), size=(s, s), fill="white"))
    pat.add(
        dwg.line(
            start=(0, 0),
            end=(0, s),
            stroke="black",
            stroke_width=cfg.hatch_stroke,
            stroke_linecap="round",
        )
    )
    dwg.defs.add(pat)

    css = f"""
    .w {{ fill: white; stroke: none; }}
    .h {{ fill: url(#h); stroke: none; }}
    .e {{ fill: none; stroke: black; stroke-width: {cfg.edge_stroke}px;
         stroke-linecap: round; stroke-linejoin: round; }}
    """
    dwg.defs.add(dwg.style(css))


def collect_faces(origin, cam2world, world2cam, cfg: Config):
    R = cam2world[:3, :3]
    rds = make_rays(cfg.viewbox, cfg.super_sampling, cfg.focal, R)
    pos, nor8, dist, hit = raycast_pixels(origin, rds, cfg.max_steps)

    idx = np.flatnonzero(hit)
    pos = pos[idx]
    nor = nor8[idx].astype(np.int32)
    dist = dist[idx].astype(np.float64)

    # Deduplicate by (cell, normal), keep one sample each.
    keys = np.concatenate([pos, nor], axis=1)
    _, u = np.unique(keys, axis=0, return_index=True)
    pos, nor, dist = pos[u], nor[u], dist[u]

    # Painter's order (far -> near).
    order = np.argsort(dist)[::-1]
    pos, nor, dist = pos[order], nor[order], dist[order]

    pts = project_faces(pos, nor, world2cam, cfg.focal, cfg.viewbox)
    eds = visible_edges(pos, nor)
    return pos, nor, pts, eds


def render(cfg: Config, ro: np.ndarray, ta: np.ndarray, roll: float = 0.3):
    cam2world = make_camera(ro, ta, roll)
    world2cam = np.linalg.inv(cam2world)

    dwg = svgwrite.Drawing(
        cfg.out_file,
        size=cfg.svg_size,
        viewBox=f"{cfg.viewbox[0]} {cfg.viewbox[1]} {cfg.viewbox[2]} {cfg.viewbox[3]}",
    )
    add_defs(dwg, cfg)

    pos, nor, pts, edges = collect_faces(ro, cam2world, world2cam, cfg)
    M = pos.shape[0]

    for i in range(M):
        quad = pts[i]  # (4,2)
        d_face = path_closed_quad(quad, cfg)
        if not d_face:
            continue

        need_hatch = int(nor[i, 2]) != 0
        dwg.add(dwg.path(d=d_face, class_=("h" if need_hatch else "w")))

        segs = [(quad[k], quad[(k + 1) & 3]) for k in range(4) if edges[i, k]]
        if segs:
            d_stroke = path_segments(segs, cfg)
            if d_stroke:
                dwg.add(dwg.path(d=d_stroke, class_="e"))

    dwg.save()


if __name__ == "__main__":
    cfg = Config()
    ro = np.array([43.2, 40.0, -41.1], np.float64)
    ta = np.array([-4.0, -4.5, 2.0], np.float64)
    render(cfg, ro, ta, roll=0.3)
