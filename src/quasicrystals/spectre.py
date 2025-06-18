"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Chiral aperiodic monotile `spectre`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

https://cs.uwaterloo.ca/~csk/spectre/
"""
import numpy as np
import cairo

N_ITERATIONS = 6
IDENTITY = cairo.Matrix()
R = cairo.Matrix(xx=-1)
TILE_NAMES = ["Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Phi", "Psi"]

COLOR_MAP = {
    "Gamma": (0.7, 0.8, 0.6),
    "Gamma1": (0.7, 0.4, 0.5),
    "Gamma2": (0.5, 0.65, 0.75),
    "Delta": (1, 1, 1),
    "Theta": (0.85, 0.2, 0.55),
    "Lambda": (0.2, 0.95, 0.66),
    "Xi": (0.9, 0.9, 0.4),
    "Pi": (0.4, 0.9, 0.9),
    "Sigma": (0, 0.2, 1),
    "Phi": (0.95, 1, 0.95),
    "Psi": (0.7, 0.3, 0.81),
}


class Vec2(np.ndarray):
    def __new__(cls, *args):
        obj = np.empty(2).view(cls)
        if len(args) == 1:
            obj[:] = args[0]
        else:
            obj[:] = args

        return obj

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]


U = Vec2(0.5, -np.sqrt(3) / 2)
V = Vec2(np.sqrt(3) / 2, 0.5)


SPECTRE_POINTS = [
    Vec2(0, 0),
    Vec2(1, 0),
    Vec2(1, 0) + U,
    Vec2(1, 0) + U + V,
    Vec2(1, 1) + U + V,
    Vec2(2, 1) + U + V,
    Vec2(3, 1) + V,
    Vec2(3, 2),
    Vec2(3, 2) - V,
    Vec2(3, 2) - U - V,
    Vec2(2, 2) - U - V,
    Vec2(1, 2) - U - V,
    Vec2(0, 2) - V,
    Vec2(0, 1),
]


def trot(ang):
    c = np.cos(ang)
    s = np.sin(ang)
    return cairo.Matrix(xx=c, xy=-s, yx=s, yy=c)


def ttrans(p):
    return cairo.Matrix(x0=p.x, y0=p.y)


def transTo(p, q):
    return ttrans(q - p)


def transVec2(M, P):
    return Vec2(M.transform_point(P.x, P.y))


def draw_spectre(ctx, T=None, ec=None, fc=None):
    ctx.move_to(*SPECTRE_POINTS[0])
    for point in SPECTRE_POINTS[1:]:
        ctx.line_to(*point)
    ctx.close_path()
    if fc is not None:
        ctx.set_source_rgb(*fc)
        ctx.fill_preserve()
    if ec is not None:
        ctx.set_source_rgb(*ec)
    else:
        ctx.set_source_rgb(0, 0, 0)

    ctx.stroke()


width = 1000
height = 1000
extent = 60
lw = 0.1
surface = cairo.SVGSurface("spectre.svg", width, height)
ctx = cairo.Context(surface)
ctx.scale(height / extent, -height / extent)
ctx.translate(0, extent)
ctx.set_line_width(lw)
ctx.set_line_cap(cairo.LINE_CAP_ROUND)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)
ctx.set_source_rgb(1, 1, 1)
ctx.paint()


def drawPolygon(T, fc):
    ctx.save()
    ctx.transform(T)
    draw_spectre(ctx, ec=(0, 0, 0), fc=fc)
    ctx.restore()


class Tile:
    def __init__(self, Vec2s, label):
        self.quad = [Vec2s[3], Vec2s[5], Vec2s[7], Vec2s[11]]
        self.label = label

    def draw(self, trans=IDENTITY):
        return drawPolygon(trans, COLOR_MAP[self.label])


class MetaTile:
    def __init__(self, geometries=[], quad=[]):
        """
        geometries: list of pairs of (Meta)Tiles and their transformations
        quad: MetaTile quad Vec2s
        """
        self.geometries = geometries
        self.quad = quad

    def draw(self, metatile_transformation=IDENTITY):
        """
        recursively expand MetaTiles down to Tiles and draw those
        """
        [
            shape.draw(shape_transformation * metatile_transformation)
            for shape, shape_transformation in self.geometries
        ]


def buildSpectreBase():
    spectre_base_cluster = {
        label: Tile(SPECTRE_POINTS, label) for label in TILE_NAMES if label != "Gamma"
    }
    mystic = MetaTile(
        [
            [Tile(SPECTRE_POINTS, "Gamma1"), IDENTITY],
            [
                Tile(SPECTRE_POINTS, "Gamma2"),
                trot(np.pi / 6) * ttrans(SPECTRE_POINTS[8]),
            ],
        ],
        [SPECTRE_POINTS[3], SPECTRE_POINTS[5], SPECTRE_POINTS[7], SPECTRE_POINTS[11]],
    )
    spectre_base_cluster["Gamma"] = mystic

    return spectre_base_cluster


def buildSupertiles(tileSystem):
    """
    iteratively build on current system of tiles
    tileSystem = current system of tiles, initially built with buildSpectreBase()
    """

    # First, use any of the nine-unit tiles in tileSystem to obtain
    # a list of transformation matrices for placing tiles within
    # supertiles.
    quad = tileSystem["Delta"].quad

    transformation_rules = [
        [60, 3, 1],
        [0, 2, 0],
        [60, 3, 1],
        [60, 3, 1],
        [0, 2, 0],
        [60, 3, 1],
        [-120, 3, 3],
    ]

    transformations = [IDENTITY]
    total_angle = 0
    rotation = IDENTITY
    transformed_quad = list(quad)

    for _angle, _from, _to in transformation_rules:
        if _angle != 0:
            total_angle += _angle
            rotation = trot(np.deg2rad(total_angle))
            transformed_quad = [transVec2(rotation, p) for p in quad]

        ttt = transTo(transformed_quad[_to], transVec2(transformations[-1], quad[_from]))
        transformations.append(rotation * ttt)

    transformations = [transformation * R for transformation in transformations]

    # Now build the actual supertiles, labelling appropriately.
    super_rules = {
        "Gamma": ["Pi", "Delta", None, "Theta", "Sigma", "Xi", "Phi", "Gamma"],
        "Delta": ["Xi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Phi", "Gamma"],
        "Theta": ["Psi", "Delta", "Pi", "Phi", "Sigma", "Pi", "Phi", "Gamma"],
        "Lambda": ["Psi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Phi", "Gamma"],
        "Xi": ["Psi", "Delta", "Pi", "Phi", "Sigma", "Psi", "Phi", "Gamma"],
        "Pi": ["Psi", "Delta", "Xi", "Phi", "Sigma", "Psi", "Phi", "Gamma"],
        "Sigma": ["Xi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Lambda", "Gamma"],
        "Phi": ["Psi", "Delta", "Psi", "Phi", "Sigma", "Pi", "Phi", "Gamma"],
        "Psi": ["Psi", "Delta", "Psi", "Phi", "Sigma", "Psi", "Phi", "Gamma"],
    }
    super_quad = [
        transVec2(transformations[6], quad[2]),
        transVec2(transformations[5], quad[1]),
        transVec2(transformations[3], quad[2]),
        transVec2(transformations[0], quad[1]),
    ]

    return {
        label: MetaTile(
            [
                [tileSystem[substitution], transformation]
                for substitution, transformation in zip(substitutions, transformations)
                if substitution
            ],
            super_quad,
        )
        for label, substitutions in super_rules.items()
    }


shapes = buildSpectreBase()
for _ in range(N_ITERATIONS):
    shapes = buildSupertiles(shapes)

shapes["Delta"].draw()
surface.finish()
