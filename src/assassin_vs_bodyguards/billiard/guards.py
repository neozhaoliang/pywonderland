from .vector import Vec2
from .transform import triangle_to_cartesian, D_inf, D2, D3
from .polygon import HEXAGON_CENTER


def compute_guards_positions_parallel(room, assin, target):
    targets = []
    for i in range(4):
        targets.append(D_inf[i](target))
    guards = []
    for t in targets:
        midpoint = assin.midpoint(t)
        _, g = room.get_bounce_trajectory(assin, midpoint)
        guards.append(g)
    return guards


def compute_guards_positions_square(room, assin, target):
    targets = []
    for i in range(4):
        virtual_target = D2[i](target)
        for i in range(2):
            for j in range(2):
                targets.append(virtual_target + Vec2(2 * i, 2 * j))

    guards = []
    for t in targets:
        midpoint = assin.midpoint(t)
        _, g = room.get_bounce_trajectory(assin, midpoint)
        guards.append(g)
    return guards


def compute_guards_positions_triangle(room, assin, target):
    targets = []
    for i in range(6):
        virtual_target = D3[i](target)
        for i, j in [(0, 0), (-2, 1), (-1, 2), (1, 1)]:
            xy = triangle_to_cartesian(i, j)
            targets.append(virtual_target + xy)

    guards = []
    for t in targets:
        midpoint = assin.midpoint(t)
        _, g = room.get_bounce_trajectory(assin, midpoint)
        guards.append(g)
    return guards


def compute_guards_positions_hexagon(room, assin, target):
    targets = []
    for i in range(6):
        virtual_target = D3[i](target)
        for i, j in [(0, 0), (-2, 1), (-1, 2), (1, 1)]:
            xy = triangle_to_cartesian(i, j)
            targets.append(virtual_target + xy)

    guards = []
    for t in targets:
        midpoint = assin.midpoint(t)
        _, g = room.get_bounce_trajectory(assin, midpoint)
        for i in range(6):
            p = g.copy()
            p -= HEXAGON_CENTER
            p = D3[i](p)
            p += HEXAGON_CENTER
            guards.append(p)
    return guards
