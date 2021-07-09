#version 130

uniform vec3          iResolution;
uniform float         iTime;
uniform float         iTimeDelta;
uniform vec4          iMouse;
uniform vec4          iDate;
uniform sampler2D     iChannel0;
uniform sampler2D     iChannel1;
uniform sampler2D     iChannel2;
uniform int           AA;

out vec4 fragColor;

#define RED vec3(0.8, 0, 0)
#define BLUE vec3(0, 0, 0.8)
#define GREEN vec3(0, 0.5, 0)
#define CYAN vec3(0, 0.5, 0.8)
#define BLACK vec3(0)
#define WHITE vec3(1)
#define GRAY vec3(.3)
#define LIGHTGRAY vec3(.8)
#define LIGHTRED vec3(0.9, 0.5, 0.5)
#define LIGHTBLUE vec3(0.5, 0.5, 0.9)

#define REG_PQR_PROJ  ivec2(0,0)
#define REG_MOUSE     ivec2(1,0)
#define REG_GENERATOR ivec2(2,0)
#define REG_FLAGS     ivec2(3,0)
#define REG_CENTER    ivec2(4,0)
#define REG_TIME      ivec2(5,0)
#define REG_UI_STATE  ivec2(6,0)
#define REG_ROTATE    ivec2(7,0)
#define REG_WRAP      ivec2(8,0)

#define STYLE_DRAW_POLYGONS   0x01
#define STYLE_DRAW_GENERATOR  0x02
#define STYLE_DRAW_TRIANGLES  0x04
#define STYLE_DRAW_CIRCLES    0x08
#define STYLE_SHADE_TRIANGLES 0x10
#define STYLE_FIX_COLOR       0x20

#define FACE_COLOR_PRIMARY    0
#define FACE_COLOR_RAINBOW    1
#define FACE_COLOR_RANDOM     2

#define LOADC(c, reg) texelFetch(c, reg, 0)
#define LOAD(reg) texelFetch(iChannel0, reg, 0)

#define LOAD1(reg) LOAD(reg).x
#define LOAD2(reg) LOAD(reg).xy
#define LOAD3(reg) LOAD(reg).xyz
#define LOAD4(reg) LOAD(reg)

#define PROJ_DISK     0
#define PROJ_HALF     1
#define PROJ_BAND     2
#define PROJ_INV_DISK 3
#define PROJ_ORTHO    4
#define PROJ_KLEIN    5

#define NUM_PROJ      6.

#define CLAMP_ABS(x, m) clamp((x), -(m), (m))

#define TRI_NEXT(i)   ((2 + (i)*(5 - 3*(i)))/2)
#define TRI_LAST(i,j) (3 - (i) - (j))

#define PI 3.141592653589793

#define BIT_VERT_IS_FACE     0
#define BIT_PERP_HAS_LENGTH  3
#define BIT_PERP_SPLITS_EDGE 6

#define CLEAR_BIT(flags, bit, idx) (flags) &= ~(1 << ((bit) + (idx)))
#define QUERY_BIT(flags, bit, idx) (((flags) & (1 << ((bit)+(idx)))) != 0)

#define PQR_MIN 2.
#define PQR_MAX 9.

#define PCOLOR vec3(1, 0, 0)
#define RCOLOR vec3(1, 1, 0)
#define QCOLOR vec3(0, 0, 1)

#define CENTER_STATIONARY 0.
#define CENTER_SWEEPING   1.
#define CENTER_ROTATING   2.
#define CENTER_GYRATING   3.


const mat3 VCOLORS = mat3(PCOLOR, QCOLOR, RCOLOR);

// global projection variables
int activeProj;

float px;
float lineSize;

// global UI variables
float uiSize;
vec3 uiBorder;

bool isConformal;
bool shouldDrawDisk;

vec4 sceneBox;
vec4 uiBox;

vec2 sceneOrigin;

vec4 insetBox;
vec4 iconsBox;
vec4 pqrBox;
vec4 projBox;
float projSize;

float iconSize;
float pqrSize;

// global vars for inset triangle
mat3 insetEdges;
mat3 insetBisectors;
mat3 insetVerts;
mat3 insetEdgePoints;

vec2 insetOrigin;
float insetPx;
mat2 insetR;
float insetPointSize;

//////////////////////////////////////////////////////////////////////
// rotate vector by 90 degrees

vec2 perp(vec2 p) {
    return vec2(-p.y, p.x);
}

//////////////////////////////////////////////////////////////////////
// distance to 2D box given by (ctr, radius)

float boxDist(vec2 p, vec4 b) {
    p = abs(p - b.xy) - b.zw;
    return max(p.x, p.y);
}

bool insideBox(vec2 p, vec4 b) {
    return boxDist(p, b) <= 0.;
}

//////////////////////////////////////////////////////////////////////
// general hyperbolic functions

// return p but with z flipped
vec3 hyperConj(vec3 p) {
    return vec3(p.xy, -p.z);
}

// hyperDot(u, v) = dot(u, hyperConj(v)) = dot(hyperConj(u), v)
float hyperDot(vec3 u, vec3 v) {
    return dot(u.xy, v.xy) - u.z*v.z;
}

// return cross product with negative z
// hyperDot(x, hyperCross(x, y)) = hyperDot(y, hyperCross(x, y)) = 0
vec3 hyperCross(vec3 x, vec3 y) {
    return hyperConj(cross(x, y));
}

// flip point if necessary to lie in upper hyperboloid and normalize it
// so that hyperDot(u, u) = -1
vec3 hyperNormalizeP(vec3 u) {
    float s = u.z < 0. ? -1. : 1.;
    return u * (s / sqrt(-hyperDot(u, u)));
}

// normalize geodesic so that hyperDot(v, v) = 1
vec3 hyperNormalizeG(vec3 v) {
    return v / sqrt(hyperDot(v, v));
}

// distance between two points
float hyperDistPP(vec3 u, vec3 v) {
    return acosh(max(1.0, -hyperDot(u, v)));
}

// distance between point and line
float hyperDistPG(vec3 u, vec3 v) {
    return asinh(hyperDot(u, v));
}

// construct geodesic from two points
vec3 geodesicFromPoints(vec3 u, vec3 v) {
    return hyperNormalizeG(hyperCross(u,v));
}

// construct geodesic perpendicular to l passing thru x
#define geodesicPerpThruPoint(l,x) geodesicFromPoints(l,x)

// intersection of two geodesics - undefined if they don't intersect
vec3 intersectGG(vec3 l, vec3 f) {
    return hyperNormalizeP(hyperCross(l, f));
}

// construct bisector of two points
vec3 hyperBisector(vec3 u, vec3 v) {
    return hyperNormalizeG(hyperCross(u+v, hyperCross(u, v)));
}

// reflect point across geodesic
vec3 reflectPG(vec3 x, vec3 l) {
    return x - (2.*hyperDot(x,l)/hyperDot(l,l))*l;
}

// translate the origin to a specific point
vec3 hyperTranslate(vec3 p, vec3 t) {

    if (dot(t.xy, t.xy) < 1e-7) { return p; }

    vec3 flipz = vec3(1, 1, -1);
    vec3 o = vec3(0, 0, 1);

    vec3 tp1 = t+o;
    vec3 tx1 = cross(t, o) * flipz;

    // bisector of t and origin
    vec3 b = cross(t+o, tx1);

    // reflect across bisector
    p -= (2.*hyperDot(p, b)/hyperDot(b,b))*b;

    // reflect direction of t
    vec2 n = t.xy;
    p.xy = p.xy - (2.*dot(n, p.xy)/dot(n,n))*n;

    return p;

}

// construct angular bisector at intersection of l1 & l2
vec3 hyperAngleBisector(vec3 l1, vec3 l2) {
    return hyperNormalizeG(l1 - l2);
}

// set up a triangle with angles pi/p, pi/q, pi/r, anchored at origin
mat3 setupTriangle(vec3 pqr) {

    vec3 angles = PI/pqr;

    vec3 cpqr = cos(angles);
    float sp = sin(angles.x);

    float a = (cpqr.x*cpqr.y + cpqr.z)/sp;
    float b = cpqr.y;
    float c = sqrt(a*a + b*b - 1.);

    return mat3(vec3(-b, a, c),
                vec3(-cpqr.x, -sp, 0),
                vec3(1, 0, 0));

}

// construct triangle vertices from edges
mat3 hyperTriVerts(mat3 edges) {

    mat3 verts;

    for (int i=0; i<3; ++i) {
        int j = TRI_NEXT(i);
        int k = TRI_LAST(i, j);
        verts[i] = intersectGG(edges[j], edges[k]);
    }

    return verts;

}

// construct angle bisectors at vertices of triangle
mat3 hyperTriAngleBisectors(mat3 edges) {

    mat3 bisectors;

    for (int i=0; i<3; ++i) {
        int j = TRI_NEXT(i);
        int k = TRI_LAST(i, j);
        bisectors[i] = hyperAngleBisector(edges[j], edges[k]);
    }

    return bisectors;

}

// construct perpendiculars to edges passing thru generator
mat3 hyperTriPerps(mat3 edges, vec3 generator) {

    mat3 perps;

    for (int i=0; i<3; ++i) {
        perps[i] = geodesicPerpThruPoint(edges[i], generator);
    }

    return perps;

}


//////////////////////////////////////////////////////////////////////
// complex math functions

vec2 complexLog(vec2 z) {
    return vec2(log(length(z)), atan(z.y, z.x));
}

vec2 complexExp(vec2 z) {
    return exp(z.x) * vec2(cos(z.y), sin(z.y));
}

vec2 complexInv(vec2 z) {
    return vec2(z.x, -z.y) / dot(z, z);
}

vec2 complexMul(vec2 a, vec2 b)  {
    return vec2(a.x*b.x - a.y*b.y, a.x*b.y + a.y*b.x);
}

vec2 complexAtanh(vec2 z) {
    return 0.5*(complexLog(vec2(1, 0) + z) - complexLog(vec2(1, 0) - z));
}

vec2 complexTanh(vec2 z) {

    vec2 e2z = complexExp(2.*z);

    vec2 num = e2z - vec2(1, 0);
    vec2 denom = e2z + vec2(1, 0);

    return complexMul(num, complexInv(denom));

}

//////////////////////////////////////////////////////////////////////
// Poincare disk projection functions

float diskMetric(vec2 d) {
    return 0.5*(1. - dot(d, d));
}

bool diskPointValid(vec2 d) {
    return dot(d, d) < 1.;
}

vec2 diskProjValid(vec2 d, bool pad) {

    float DISK_MAX = pad ? 0.95 : 0.875;

    float l = length(d);
    if (l > DISK_MAX) { d *= DISK_MAX/l; }
    return d;

}

vec2 diskFromHyperboloid(vec3 p) {
    return p.xy / (1. + p.z);
}

vec3 hyperboloidFromDisk(vec2 d) {
    float s = dot(d, d);
    return vec3(2.*d, 1.+s) / (1. - s);
}

//////////////////////////////////////////////////////////////////////
// Poincare half-plane projection functions

bool halfPointValid(vec2 h) {
    return h.y > 0.;
}

vec2 halfProjValid(vec2 h, bool pad) {
    float ey = pad ? 0.01 : 0.1;
    return vec2(h.x, max(h.y, ey));
}

float halfMetric(vec2 h) {
    return h.y;
}

vec2 halfFromDisk(vec2 d) {

    float dx2 = d.x*d.x;
    float dy1 = (d.y - 1.);
    float k = 1./(dx2 + dy1*dy1);

    float hx = 2.*d.x*k;
    float hy = -(dx2 + dy1*(d.y + 1.))*k;

    return vec2(hx, hy);

}

vec2 diskFromHalf(vec2 h) {

    float hx2 = h.x*h.x;
    float hy1 = (h.y + 1.);
    float k = 1./(hx2 + hy1*hy1);

    float dx = 2.*h.x*k;
    float dy = (hx2 + (h.y - 1.)*hy1)*k;

    return vec2(dx, dy);

}

//////////////////////////////////////////////////////////////////////
// Band projection functions

bool bandPointValid(vec2 b) {
    return abs(b.y) < 1.;
}

vec2 bandProjValid(vec2 b, bool pad) {
    const vec2 BAND_LIMITS = vec2(1.125, 0.85);
    return CLAMP_ABS(b, BAND_LIMITS + (pad ? 0.05 : 0.));
}

#define BAND_SCL (4./PI)

float bandMetric(vec2 b) {
    return (2./PI)*cos(b.y*0.5*PI);
}

vec2 bandFromDisk(vec2 z) {
    return BAND_SCL*complexAtanh(z);
}

vec2 diskFromBand(vec2 z) {
    return complexTanh(z / BAND_SCL);
}

//////////////////////////////////////////////////////////////////////
// inverted poincare disk projection functions

vec2 invertDisk(vec2 p) {
    return p / dot(p, p);
}

bool invDiskPointValid(vec2 p) {
    return dot(p, p) > 1.;
}

vec2 invDiskProjValid(vec2 p, bool pad) {

    float DISK_MIN = pad ? 1.15 : 1.25;

    if (p == vec2(0)){
        return vec2(0, 1.65);
    }


    float l = length(p);

    return l < DISK_MIN ? p*DISK_MIN/l : p;

}

float invDiskMetric(vec2 p) {
    float d = dot(p, p);
    return 0.5*(1. - 1./d)*d;
}

//////////////////////////////////////////////////////////////////////
// orthographic projection functions

vec2 orthoFromHyperboloid(vec3 p) {
    return p.xy;
}

vec3 hyperboloidFromOrtho(vec2 o) {
    return vec3(o, sqrt(1. + dot(o, o)));
}

mat2x3 hyperboloidFromOrthoJacobian(vec2 o) {

    float s = 1./sqrt(1. + dot(o, o));

    vec3 j0 = vec3(1, 0, o.x*s);
    vec3 j1 = vec3(0, 1, o.y*s);

    return mat2x3(j0, j1);

}

float orthoMetric(vec2 o) {

    float w = 1./(1. + dot(o, o));

	// hyper-dot products of jacobian above
    float j00 = 1. - o.x*o.x*w;
    float j01 = -o.x*o.y*w;
    float j11 = 1. - o.y*o.y*w;

    // inspired by equation 1.4 of Arvo 2001
    float dA = sqrt(j00*j11 - j01*j01);

    return 1.0 / sqrt(dA);


}

//////////////////////////////////////////////////////////////////////
// klein projection functions

vec2 kleinFromDisk(vec2 d) {
    return 2.*d / (1. + dot(d, d));
}

vec2 diskFromKlein(vec2 k) {
    float z = sqrt(1. - dot(k, k));
    vec2 d = k / (1. + z);
    return d;
}

mat2 kleinFromDiskJacobian(vec2 d) {

	vec2 d2 = d*d;

    float z = (1. + dot(d,d));
    float h = 2.0/(z*z);

    float m00 = (-d2.x + d2.y + 1.);
    float m11 = (d2.x - d2.y + 1.);

    float m01 = -2.*d.x*d.y;

    return mat2(m00, m01, m01, m11)*h;

}

float kleinMetric(vec2 k) {

    vec2 d = diskFromKlein(k);

    vec2 d2 = d*d;

    float z = (1. + dot(d,d));

    float m00 = (-d2.x + d2.y + 1.);
    float m11 = (d2.x - d2.y + 1.);

    // determinant of jacobian above
    return diskMetric(d) * sqrt(2.*m00*m11 - 4.*d2.x*d2.y)/z;

}

//////////////////////////////////////////////////////////////////////
// generic projection functions - just call functions above
// depending on activeProj

vec2 fromHyperboloid(vec3 p) {

    if (activeProj == PROJ_DISK) {
        return diskFromHyperboloid(p);
    } else if (activeProj == PROJ_HALF) {
        return halfFromDisk(diskFromHyperboloid(p));
    } else if (activeProj == PROJ_BAND) {
        return bandFromDisk(diskFromHyperboloid(p));
    } else if (activeProj == PROJ_INV_DISK) {
        return invertDisk(diskFromHyperboloid(p));
    } else if (activeProj == PROJ_ORTHO) {
        return orthoFromHyperboloid(p);
    } else if (activeProj == PROJ_KLEIN) {
        return kleinFromDisk(diskFromHyperboloid(p));
    }

}

vec3 toHyperboloid(vec2 q) {

    if (activeProj == PROJ_DISK) {
        return hyperboloidFromDisk(q);
    } else if (activeProj == PROJ_HALF) {
        return hyperboloidFromDisk(diskFromHalf(q));
    } else if (activeProj == PROJ_BAND) {
        return hyperboloidFromDisk(diskFromBand(q));
    } else if (activeProj == PROJ_INV_DISK) {
        return hyperboloidFromDisk(invertDisk(q));
    } else if (activeProj == PROJ_ORTHO) {
        return hyperboloidFromOrtho(q);
    } else {
        return hyperboloidFromDisk(diskFromKlein(q));
    }

}

bool pointValid(vec2 q) {

    if (activeProj == PROJ_DISK || activeProj == PROJ_KLEIN) {
        return diskPointValid(q);
    } else if (activeProj == PROJ_INV_DISK) {
        return invDiskPointValid(q);
    } else if (activeProj == PROJ_HALF) {
        return halfPointValid(q);
    } else if (activeProj == PROJ_BAND) {
        return bandPointValid(q);
    } else {
        return true;
    }

}

vec2 projValid(vec2 q, bool pad) {

    if (activeProj == PROJ_DISK || activeProj == PROJ_KLEIN) {
        return diskProjValid(q, pad);
    } else if (activeProj == PROJ_INV_DISK) {
        return invDiskProjValid(q, pad);
    } else if (activeProj == PROJ_HALF) {
        return halfProjValid(q, pad);
    } else if (activeProj == PROJ_BAND) {
        return bandProjValid(q, pad);
    } else {
        return q;
    }

}

float metric(vec2 q) {

    if (activeProj == PROJ_DISK) {

        return diskMetric(q);

    } else if (activeProj == PROJ_HALF) {

        return halfMetric(q);

    } else if (activeProj == PROJ_BAND) {

        return bandMetric(q);

    } else if (activeProj == PROJ_INV_DISK) {

        return invDiskMetric(q);

    } else if (activeProj == PROJ_KLEIN) {

        return kleinMetric(q);

    } else { // PROJ_ORTHO

        return orthoMetric(q);

    }

}

//////////////////////////////////////////////////////////////////////
// pixel coords <-> scene coords

vec2 sceneFromFrag(vec2 f) {
    return (f - sceneOrigin) * px;
}

vec2 fragFromScene(vec2 s) {
    return s / px + sceneOrigin;
}

//////////////////////////////////////////////////////////////////////
// UI setup functions

vec4 flipBox(vec4 box, vec2 dims) {

    box = box.yxwz;
    box.xy = dims.yx - box.xy;

    return box;

}

void setupUI(vec2 dims, bool flip, float showUI) {

    uiSize = 0.25*dims.x;

    float deltaUI = (1.0 - showUI) * uiSize;

    uiBox.xy = 0.5*vec2(uiSize, dims.y);
    uiBox.zw = uiBox.xy;

    vec2 sceneSize = vec2(dims.x - uiSize, dims.y);

    sceneBox.xy = vec2(uiSize + 0.5*sceneSize.x, 0.5*dims.y);
    sceneBox.zw = 0.5*sceneSize;

    uiBox.x -= deltaUI;

    sceneBox.x -= 0.5*deltaUI;
    sceneBox.z += 0.5*deltaUI;

    vec2 insetSize = vec2(uiSize, dims.y*(flip ? 0.2 : 0.3333));

    float remainingLength = dims.y - insetSize.y;

    vec2 sel = flip ? vec2(1, 0) : vec2(0, 1);

    insetBox.xy = vec2(uiBox.x, 0.5*insetSize.y);
    insetBox.zw = 0.5*insetSize;

    float iconsLength = dot(sel, vec2(6, 6));
    float pqrLength = dot(sel, vec2(4, 5));
    float projLength = dot(sel, vec2(8, 2));
    float gapLength = dot(sel, vec2(0.3, 0.5));

    float totalLength = iconsLength + pqrLength + projLength + 3.*gapLength;

    float scl = remainingLength / totalLength;

    iconsLength *= scl;
    pqrLength *= scl;
    projLength *= scl;
    gapLength *= scl;

    iconsBox = vec4(uiBox.x, dims.y - 0.5*iconsLength, 0.5*uiSize, 0.5*iconsLength);

    pqrBox = vec4(uiBox.x, dims.y - iconsLength - 0.5*pqrLength - gapLength,
                  0.5*uiSize, 0.5*pqrLength);


    projBox = vec4(uiBox.x, dims.y - iconsLength - pqrLength - 0.5*projLength - 2.*gapLength,
                   0.5*uiSize, 0.5*projLength);

    uiBorder = vec3(1, 0, -uiSize+deltaUI);

    if (flip) {
        uiBox = flipBox(uiBox, dims);
        sceneBox = flipBox(sceneBox, dims);
        insetBox = flipBox(insetBox, dims);
        iconsBox = flipBox(iconsBox, dims);
        pqrBox = flipBox(pqrBox, dims);
        projBox = flipBox(projBox, dims);
        uiBorder = vec3(0, -1, dims.x-uiSize+deltaUI);
    }

    iconSize = min(0.15*iconsBox.z, 0.32*iconsBox.w);
    pqrSize = min(0.65*pqrBox.z, 0.75*pqrBox.w);
    projSize = min(0.13*projBox.z, projBox.w);

    sceneOrigin = sceneBox.xy;

}

//////////////////////////////////////////////////////////////////////
// initialize the viewport transformation & UI globals

void setupProjection(in int p, vec2 res, float showUI) {

    bool flip = res.y > res.x;
    setupUI(flip ? res.yx : res.xy, flip, showUI);

    activeProj = p;

    float smin = min(sceneBox.z, sceneBox.w);
    lineSize = 0.008 * smin;

    if (activeProj == PROJ_HALF) {
        px = 1.0 / sceneBox.w;
        sceneOrigin.y = -0.01 / px;
    } else if (activeProj == PROJ_INV_DISK) {
        px = 3.0 / smin;
        lineSize *= 0.125;
    } else if (activeProj == PROJ_ORTHO) {
        px = 3.0 / smin;
    } else if (activeProj == PROJ_BAND) {
        px = 0.98 / sceneBox.w;
    } else { // klein/disk
        px = 1.04 / smin;
    }

    lineSize *= px;

    isConformal = (activeProj < PROJ_ORTHO);

    shouldDrawDisk = (activeProj == PROJ_DISK ||
                      activeProj == PROJ_INV_DISK ||
                      activeProj == PROJ_KLEIN);

    if (isConformal) {

        vec2 uv = projValid(sceneFromFrag(0.5*res.xy), false);
        float m = metric(uv);
        lineSize /= m;

    }

}

//////////////////////////////////////////////////////////////////////
// setup the inset triangle - a little expensive to call

void setupInset(mat3 edges) {

    for (int i=0; i<3; ++i) {
        insetEdges[i] = vec3(-perp(edges[i].xy), edges[i].z);
    }

    insetBisectors = hyperTriAngleBisectors(insetEdges);
    vec3 center = intersectGG(insetBisectors[0], insetBisectors[1]);

    vec3 centerInv = -hyperConj(center);

    for (int i=0; i<3; ++i) {
        insetEdges[i] = hyperTranslate(insetEdges[i], centerInv);
        insetBisectors[i] = hyperTranslate(insetBisectors[i], centerInv);
        insetEdgePoints[i] = intersectGG(insetEdges[i], insetBisectors[i]);
    }

    insetVerts = hyperTriVerts(insetEdges);

    vec2 insetVertsDisk[3];

    for (int i=0; i<3; ++i) {
        insetVertsDisk[i] = diskFromHyperboloid(insetVerts[i]);
    }

    vec2 n = normalize(insetVertsDisk[1] - insetVertsDisk[0]);

    insetR = mat2(n, perp(n));

    vec2 dmin = vec2(1e5);
    vec2 dmax = vec2(-1e5);

    for (int i=0; i<3; ++i) {
        dmin = min(dmin, insetVertsDisk[i]*insetR);
        dmax = max(dmax, insetVertsDisk[i]*insetR);
    }

    insetPointSize = 0.1*min(insetBox.z, insetBox.w);

    vec2 drad = 0.5*(dmax-dmin);
    vec2 dscl = drad / (insetBox.zw - 3.0*insetPointSize);

    insetPx = max(dscl.x, dscl.y);

    insetOrigin = insetBox.xy - 0.5*(dmax+dmin)/insetPx;

}

// Poincare disk from inset box
vec2 diskFromInset(vec2 fragCoord) {
    return insetR*((fragCoord - insetOrigin)*insetPx);
}

//////////////////////////////////////////////////////////////////////
// box locations for UI interactions

vec4 iconUIBox(ivec2 idx) {

    vec2 iconCtr = iconsBox.xy;

    iconCtr = floor(iconCtr+0.5);

    vec2 scl = vec2(2.5*iconSize, 3.*iconSize);
    iconCtr += vec2(float(idx.x), float(-idx.y))*scl + vec2(-2., 0.5)*scl;

    return vec4(iconCtr, vec2(iconSize));

}

vec4 digitUIBox(int idx) {

    const vec2 digitRad = vec2(0.35, 0.5);

    return vec4(pqrBox.x + (float(idx - 1))*pqrSize,
                pqrBox.y,
                digitRad*pqrSize);

}

vec4 triUIBox(int idx, float delta) {

    return vec4(digitUIBox(idx).xy + vec2(0, 0.9*delta*pqrSize),
                0.4*pqrSize, 0.3*pqrSize);

}

vec4 projUIBox(float delta) {

    return vec4(projBox.xy + vec2(delta*6.5*projSize, 0),
                0.75*projSize, 1.0*projSize);

}

mat3 inverse(mat3 m)
{
    float a00 = m[0][0], a01 = m[0][1], a02 = m[0][2];
    float a10 = m[1][0], a11 = m[1][1], a12 = m[1][2];
    float a20 = m[2][0], a21 = m[2][1], a22 = m[2][2];

    float b01 = a22 * a11 - a12 * a21;
    float b11 = -a22 * a10 + a12 * a20;
    float b21 = a21 * a10 - a11 * a20;

    float det = a00 * b01 + a01 * b11 + a02 * b21;

    return mat3(b01, (-a22 * a01 + a02 * a21), (a12 * a01 - a02 * a11),
                b11, (a22 * a00 - a02 * a20), (-a12 * a00 + a02 * a10),
                b21, (-a21 * a00 + a01 * a20), (a11 * a00 - a01 * a10)) / det;
}
