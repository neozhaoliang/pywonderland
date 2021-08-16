#version 130
#define providesInit
#define providesColor
#include "MathUtils.frag"
#include "DE-Raytracer.frag"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Compact and paracompact Hyperbolic honeycombs in H3 space
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This program draws compact/para-compact uniform hyperbolic honeycombs in
Poincaré's 3D ball model (it also works for some non-compact ones).
For a complete list of available honeycombs see

    "https://en.wikipedia.org/wiki/Uniform_honeycombs_in_hyperbolic_space"

Thanks @knighty for his fragmentarium code && help.

Some math stuff:

1. The 4D space R^4 is endowed with Minkowski inner product: for
   p=(x1, y1, z1, w1) and q=(x2, y2, z2, w2), their "hyperbolic dot" is given by

       hdot(p, q) := x1*y1 + x2*y2 * x3*y3 - x4*y4.

   This inner product has Sylvester type (3, 1), the quadratic form is Q(p) = hdot(p, p).

2. The hyperboloid are those vectors in R^4 with Q(p) = -1 (time-like). For those q with
   Q(q) > 0 we call q space-like. The hyperboloid consists of two sheets: w > 0 and w < 0.

3. The distance between two vectors p, q on the same sheet is given by

       cosh(d(p, q)) = -hdot(p, q).

4. Any geodesic line from a point p on the hyperboloid can be parameterized by

       p*cosh(t) + v*sinh(t),

   where v is a unit tangent vector at p (v must be space-like).

5. A reflection across a plane with normal `n` is given by

       ref(p) = p - 2 * hdot(p, n) * n.

   Here p is time-like and n is space-like.

6. We iteratively reflect a 4d point until it's in the fundamental domian, we get
   its distance to the initial vertex/mirrors, then use knighty's magic formula to
   estimate a `safe` distance that we can march in the 3d space. This is the most
   intriguing part in the code.


@mla has another honeycomb demo:

    https://www.shadertoy.com/view/XddyR2

@knighty's fragmentarium code:

    https://github.com/3Dickulus/Fragmentarium_Examples_Folder/tree/master/Knighty%20Collection/Hyperbolic-tesselations-named


~~~~~~~~~~~~~~~~~~~~~~~~~~~~
List of available honeycombs


***9 compact ones***

(5, 2, 2, 3, 2, 5), (3, 2, 2, 5, 2, 3), (4, 2, 2, 5, 2, 3), (5, 2, 2, 4, 2, 3)

  5       5            5            4       5        5       4
o---o---o---o    o---o---o---o    o---o---o---o    o---o---o---o


(4, 2, 3, 3, 2, 4), (5, 2, 3, 3, 2, 4), (5, 2, 3, 3, 2, 5), (5, 2, 2, 3, 3, 2), (5, 2, 3, 3, 2, 3)

                                             o
  o---o        o---o        o---o        5  /       o---o
4 |   | 4    5 |   | 4    5 |   | 5    o---o      5 |   |
  o---o        o---o        o---o           \       o---o
                                             o

***paracompact ones***


(6, 2, 2, 2, 3, 3), (3, 2, 2, 2, 3, 6), (6, 2, 2, 2, 3, 6), (3, 2, 2, 2, 6, 3)

  6                        6        6       6            6
o---o---o---o    o---o---o---o    o---o---o---o    o---o---o---o
A   B   D   C    A   B   D   C    A   B   D   C    A   B   D   C


(4, 2, 2, 2, 4, 4), (4, 2, 2, 2, 4, 3), (3, 2, 2, 2, 4, 4)

  4   4   4        4   4                4   4
o---o---o---o    o---o---o---o    o---o---o---o
A   B   D   C    A   B   D   C    A   B   D   C


(6, 2, 2, 2, 3, 5), (5, 2, 2, 2, 3, 6), (4, 2, 2, 2, 3, 6), (6, 2, 2, 2, 3, 4)


  6       5        5       6        4       6        6       4
o---o---o---o    o---o---o---o    o---o---o---o    o---o---o---o
A   B   D   C    A   B   D   C    A   B   D   C    A   B   D   C


(4, 2, 2, 3, 4, 2), (4, 2, 4, 3, 2, 3), (4, 2, 4, 3, 2, 4), (3, 2, 6, 4, 2, 3), (3, 2, 6, 5, 2, 3)

                 B
A o              o            4
  4\           4/ \       A o---o B    A o---o B    A o---o B
    o---o    A o   o C    4 |   |      6 |   | 4    6 |   | 5
  4/B   C      4\ /       D o---o C    D o---o C    D o---o C
  o              o            4
  D              D


(3, 2, 2, 3, 3, 3), (3, 2, 3, 4, 3, 2), (3, 2, 3, 5, 3, 2)

      o C          o A          o A
A   B/|      C 4 B/|      C 5 B/|
o---o |      o---o |      o---o |
     \|           \|           \|
      o D          o D          o D


(3, 2, 3, 3, 3, 3)

    B
    o
   /|\
A o | o C
   \|/
    o
    D
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uniform vec3 Eye;
uniform vec3 Target;

#group HTess-Color
uniform vec3 segAColor; color[0.0,0.0,0.0]
uniform vec3 segBColor; color[0.0,0.0,0.0]
uniform vec3 segCColor; color[0.0,0.0,0.0]
uniform vec3 segDColor; color[0.0,0.0,0.0]
uniform vec3 verticesColor; color[0.0,0.0,0.0]

#group Honeycomb-Settings
uniform bool doUpperHalfSpace; checkbox[false]
uniform int AB; slider[2,5,7]
uniform int AC; slider[2,2,7]
uniform int AD; slider[2,2,7]
uniform int BC; slider[2,3,7]
uniform int BD; slider[2,2,7]
uniform int CD; slider[2,4,7]
uniform vec4 activeMirrors; slider[(0,0,0,0),(1,0,0,0),(1,1,1,1)]
uniform float vertexSize; slider[0,0.05,0.5]
uniform float edgeSize; slider[0,0.01,0.1]
uniform int Iterations; slider[0,30,1000]
uniform float CSphRad;  slider[0,0.99995,1]

// normal vectors of the four mirrors
mat4 M;

mat4 V;

// the initial vertex
vec4 v0;

// cosh, sinh of the vertex radius and edge radius
float cvr, svr, csr, ssr;

// Minkowski inner product with Sylvester type (3, 1)
float hdot(in vec4 p, in vec4 q) { return dot(p.xyz, q.xyz) - p.w * q.w; }

// normalize a time-like vector <v, v> < 0
vec4 hnormalize(in vec4 p) { return p / sqrt(-hdot(p, p)); }

// reflection about a plane with normal `n`
float href(inout vec4 p, in vec4 n) {
    float k = min(0., hdot(p, n));
    p -= 2. * k * n;
    return k;
}

mat4 inverse(mat4 m) {
  float
      a00 = m[0][0], a01 = m[0][1], a02 = m[0][2], a03 = m[0][3],
      a10 = m[1][0], a11 = m[1][1], a12 = m[1][2], a13 = m[1][3],
      a20 = m[2][0], a21 = m[2][1], a22 = m[2][2], a23 = m[2][3],
      a30 = m[3][0], a31 = m[3][1], a32 = m[3][2], a33 = m[3][3],

      b00 = a00 * a11 - a01 * a10,
      b01 = a00 * a12 - a02 * a10,
      b02 = a00 * a13 - a03 * a10,
      b03 = a01 * a12 - a02 * a11,
      b04 = a01 * a13 - a03 * a11,
      b05 = a02 * a13 - a03 * a12,
      b06 = a20 * a31 - a21 * a30,
      b07 = a20 * a32 - a22 * a30,
      b08 = a20 * a33 - a23 * a30,
      b09 = a21 * a32 - a22 * a31,
      b10 = a21 * a33 - a23 * a31,
      b11 = a22 * a33 - a23 * a32,

      det = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06;

  return mat4(
      a11 * b11 - a12 * b10 + a13 * b09,
      a02 * b10 - a01 * b11 - a03 * b09,
      a31 * b05 - a32 * b04 + a33 * b03,
      a22 * b04 - a21 * b05 - a23 * b03,
      a12 * b08 - a10 * b11 - a13 * b07,
      a00 * b11 - a02 * b08 + a03 * b07,
      a32 * b02 - a30 * b05 - a33 * b01,
      a20 * b05 - a22 * b02 + a23 * b01,
      a10 * b10 - a11 * b08 + a13 * b06,
      a01 * b08 - a00 * b10 - a03 * b06,
      a30 * b04 - a31 * b02 + a33 * b00,
      a21 * b02 - a20 * b04 - a23 * b00,
      a11 * b07 - a10 * b09 - a12 * b06,
      a00 * b09 - a01 * b07 + a02 * b06,
      a31 * b01 - a30 * b03 - a32 * b00,
      a20 * b03 - a21 * b01 + a22 * b00) / det;
}

void init() {
    float c01 = -cos(PI / float(AB));
    float c02 = -cos(PI / float(AC));
    float c03 = -cos(PI / float(AD));
    float c12 = -cos(PI / float(BC));
    float c13 = -cos(PI / float(BD));
    float c23 = -cos(PI / float(CD));

    vec4 A, B, C, D;
    // find the reflection mirrors A, B, C, D.
    // A can be always chosen as x-axis
    A = vec4(1, 0, 0, 0);

    B = vec4(c01, sqrt(1. - c01*c01), 0., 0.);

    C = vec4(c02, 0, 0, 0);
    C.y = (c12 - C.x * B.x) / B.y;
    C.z = sqrt(abs(1. - dot(C.xy, C.xy))); // avoid rounding error in paracompact case

    D = vec4(c03, 0, 0, 0);
    D.y = (c13 - D.x * B.x) / B.y;
    D.z = (c23 - dot(D.xy, C.xy) ) / C.z;
    // !important: if you want to make the fundamental chamber lie in the upper
    // sheet of the hyperboloid then you must use "-" sign here.
    D.w = -sqrt(abs(dot(D.xyz, D.xyz) - 1.));

    vec4 H = vec4(1, 1, 1, -1);
    mat4 Minv = inverse(mat4(H*A, H*B, H*C, H*D));
    v0 = hnormalize(activeMirrors * Minv);
    vec4 vA = hnormalize(Minv[0]);
    vec4 vB = hnormalize(Minv[1]);
    vec4 vC = hnormalize(Minv[2]);
    vec4 vD = hnormalize(Minv[3]);
    M = mat4(A, B, C, D);
    V = mat4(vA, vB, vC, vD);
    // cosh(vradius), sinh(vradius), cosh(sradius), sinh(sradius)
    cvr = cosh(vertexSize); svr = sinh(vertexSize);
    csr = cosh(edgeSize); ssr = sinh(edgeSize);

}

bool fold(inout vec4 p) {
    float k;
    for(int i = 0; i < Iterations; i++) {
        k = 0.;
        p.x = abs(p.x);
        k += href(p, M[1]);
        k += href(p, M[2]);
        k += href(p, M[3]);
        // break as soon as we find it's already in the fundamental domain
        if(k == 0.) return true;
    }
    return false;
}

// knighty's conservative distance conversion from hyperboloid to 3d flat distance.
// for a 3d point p, it's lifted to a 4d point q on the hyperboloid:
//
//        2p     1+r^2
// q = ( -----,  ----- ).
//       1-r^2   1-r^2
//
// any point with distance d (ca=cosh(d),sa=sinh(d)) to q can be written as q*ca + v*sa,
// wheren v is a unit tangent vector at q. We want v look like (sp, t).
// so we have two unknowns (s, t) and two equations:

// 1. s^2 * r^2 - t^2 = 1  (tangent vector must be space-like)
// 2. 2*s/(1-r^2)*r^2 - (1+r^2)/(1-r^2)*t = 0 (definition of tangent vector at q)

// solve for s, t we have s = (1+r^2)/(r *(1-r^2)) and t = 2*r/(1-r^2).
// hence the point we choose to project to 3d is
// ([ 2*ca/(1-r^2) + (1+r^2)/(r *(1-r^2))*sa ] * p,
//  [ ca*(1+r^2)/(1-r^2) + sa*2*r/(1-r^2) ])
float knightyDD(float ca, float sa, float r) {
    float x = 1. + r * r;
    float y = 2. - x;
    return (2. * r * ca + x * sa) / (x * ca + 2. * r * sa + y) - r;
}

// if distance between p and q is a, C is a circle with radius VR centered at q,
// then the distance from p to C is a - VR, hence
// cosh(a - VR) = cosh(a)cosh(VR) - sinh(a)sinh(VR)
// sinh(a - VR) = sinh(a)cosh(VR) - cosh(a)sinh(VR)
float dVertex(vec4 p, float r) {
    float ca = -hdot(p, v0);
    float sa = 0.5 * sqrt(-hdot(p - v0, p - v0) * hdot(p + v0, p + v0));
    return knightyDD(ca * cvr - sa * svr,
                     sa * cvr - ca * svr, r);
}

// let pj = a * n + b * v0 be the projection of p onto the plane given by (v0, n).
// take Minkowski dot with p - pj by v0 and n:
// (p, n) = a + b * (v0, n)
// (p, v0) = a * (v0, n) - b
// then solve this 2x2 linear system.
float dSegment(vec4 p, vec4 n, float r) {
    float pn = hdot(p, n);
    float pv = hdot(p, v0);
    float nv = hdot(n, v0);
    float det = -1.0 - nv * nv;
    float a = (-nv * pv - pn) / det;
    float b = (pv - pn * nv) / det;
    vec4 pj = hnormalize(min(a, 0.) * n + b * v0);
    float ca = -hdot(p, pj);
    float sa = 0.5 * sqrt(-hdot(p - pj, p - pj) * hdot(p + pj, p + pj));
    return knightyDD(ca * csr - sa * ssr, sa * csr - ca * ssr, r);
}

float dSegments(vec4 p, float r) {
    float dA = dSegment(p, M[0], r);
    float dB = dSegment(p, M[1], r);
    float dC = dSegment(p, M[2], r);
    float dD = dSegment(p, M[3], r);
    return min(min(dA, dB), min(dC, dD));
}

float DE(vec3 p) {
    float h = p.z - 1e-4;
    if (doUpperHalfSpace) {
        p.z += 1.0;
        p *= 2.0 / dot(p, p);
        p.z -= 1.0;
    }
    float r = length(p);
    vec4 q = vec4(2.*p, 1.+r*r) / (1.-r*r);
    bool found = fold(q);
    orbitTrap = q;
    if (doUpperHalfSpace)
        return min(h, min(dVertex(q, r), dSegments(q, r)));
    else
        return max(r - CSphRad, min(dVertex(q, r), dSegments(q, r)));
}

vec3 baseColor(vec3 pos, vec3 normal) {
    float h = pos.z - 1e-4;
    if (doUpperHalfSpace) {
        pos.z += 1.;
        pos *= 2. / dot(pos, pos);
        pos.z -= 1.;
    }
    float r = length(pos);
    vec4 q = vec4(2.*pos, 1.+r*r) / (1.-r*r);
    bool found = fold(q);
    if (found) {
        float dA = dSegment(q, M[0], r);
        float dB = dSegment(q, M[1], r);
        float dC = dSegment(q, M[2], r);
        float dD = dSegment(q, M[3], r);
        float dV = dVertex(q, r);
        float d = min(min(min(dA, dB), min(dC, dD)), dV);
        if (doUpperHalfSpace)
            d = min(d, h);

        vec3 color = segAColor;
        if(d == dB) color = segBColor;
        if(d == dC) color = segCColor;
        if(d == dD) color = segDColor;
        if(d == dV) color = verticesColor;
        if (doUpperHalfSpace && d == h) color = BackgroundColor;
        return color;
    }
    return BackgroundColor;
}


#preset default
FOV = 0.69812
Eye = 0.026495,0.0112998,-0.0957618
Target = -0.107085,-0.025321,0.894599
Up = 0.263054,0.962318,0.0688875
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -3.21258
DetailAO = -1.55554
FudgeFactor = 1
MaxRaySteps = 461
Dither = 0.55852
NormalBackStep = 1
AO = 0,0,0,1
Specular = 0.15642
SpecularExp = 21.429
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.2069,-0.02942
CamLight = 0.878431,0.921569,0.956863,0.86524
CamLightMin = 0.81667
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 0
Fog = 0.61262
HardShadow = 0 NotLocked
ShadowSoft = 6.7626
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.67451,0.67451,0.67451
OrbitStrength = 0.77273
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,-0.6077
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0.6,0.8,1
GradientBackground = 1.29215
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 1,0,1
FloorHeight = 2
FloorColor = 1,1,1
segAColor = 0.811765,0.733333,0.32549
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.909804,0.937255,0.976471
AB = 5
AC = 2
AD = 2
BC = 3
BD = 2
CD = 4
activeMirrors = 1,0,0,0
vertexSize = 0.12
edgeSize = 0.05
Iterations = 30
CSphRad = 0.9999
#endpreset

#preset 445-1100-inside-near-the-boundary
FOV = 0.92576
Eye = 0.9,0,-8.67362e-19
Target = 1.05813,0.987049,0.0269427
Up = -0.661899,0.749444,0.014966
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -3.00965
DetailAO = -2.76108
FudgeFactor = 1
MaxRaySteps = 663
Dither = 0.55857
NormalBackStep = 0.7143
AO = 0,0,0,1
Specular = 0.23464
SpecularExp = 8.73
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.38602,-0.4995
CamLight = 0.878431,0.921569,0.956863,0.86754
CamLightMin = 0.667
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 254
Fog = 0.11484
HardShadow = 0 NotLocked
ShadowSoft = 12.072
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.7,0.7,0.7
OrbitStrength = 0.42361
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,-0.6077
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0.6,0.8,1
GradientBackground = 0.8989
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
Iterations = 1000
CSphRad = 1
segAColor = 0.666667,0.333333,1
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.705882,0.698039,0.792157
AB = 4
AC = 2
AD = 2
BC = 2
BD = 4
CD = 5
activeMirrors = 1,1,0,0
vertexSize = 0.13714
edgeSize = 0.04947
#endpreset

#preset 445-1100-outside-view
FOV = 0.71702
Eye = 0.271901,-0.244934,0.975644
Target = -0.397332,0.0402059,-0.177857
Up = -0.758603,0.509592,0.406002
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -3.21258
DetailAO = -1.55554
FudgeFactor = 1
MaxRaySteps = 461
Dither = 0.55852
NormalBackStep = 1
AO = 0,0,0,1
Specular = 0.15642
SpecularExp = 21.429
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.36764,-0.02942
CamLight = 0.878431,0.921569,0.956863,0.86524
CamLightMin = 1
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 0
Fog = 0.61262
HardShadow = 0 NotLocked
ShadowSoft = 6.7626
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.67451,0.67451,0.67451
OrbitStrength = 0.49306
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,-0.6077
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0.6,0.8,1
GradientBackground = 1.29215
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
segAColor = 0.811765,0.733333,0.32549
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.71,0.65,0.26
AB = 4
AC = 2
AD = 2
BC = 2
BD = 4
CD = 5
activeMirrors = 1,1,0,0
vertexSize = 0.12
edgeSize = 0.05
Iterations = 1000
CSphRad = 0.9999
#endpreset

#preset 444-1100-inside-near-the-boundary
FOV = 0.71702
Eye = 0.9,0,0
Target = 1.53933,0.768877,-0.00922597
Up = -0.187344,0.982282,-0.00485133
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -2.77298
DetailAO = -2.33331
FudgeFactor = 1
MaxRaySteps = 255
Dither = 0.55857
NormalBackStep = 0.7143
AO = 0,0,0,1
Specular = 0.23464
SpecularExp = 8.73
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.38602,-0.4995
CamLight = 0.878431,0.921569,0.956863,0.86754
CamLightMin = 0.667
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 254
Fog = 0.11484
HardShadow = 0 NotLocked
ShadowSoft = 12.072
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.7,0.7,0.7
OrbitStrength = 0.42361
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,-0.6077
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0.6,0.8,1
GradientBackground = 0.8989
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
Iterations = 1000
CSphRad = 1
segAColor = 0.666667,0.333333,1
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.705882,0.698039,0.792157
AB = 4
AC = 2
AD = 2
BC = 2
BD = 4
CD = 4
activeMirrors = 1,1,0,0
vertexSize = 0.08285
edgeSize = 0.03457
#endpreset


#preset 4353-1100-inside-near-the-boundary
FOV = 0.71702
Eye = 0.9,0,0
Target = 1.27297,0.927579,-0.022044
Up = -0.478915,0.877861,-3.52566e-05
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -2.77298
DetailAO = -2.33331
FudgeFactor = 1
MaxRaySteps = 255
Dither = 0.55857
NormalBackStep = 0.7143
AO = 0,0,0,1
Specular = 0.23464
SpecularExp = 8.73
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.38602,-0.4995
CamLight = 0.878431,0.921569,0.956863,0.86754
CamLightMin = 0.667
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 254
Fog = 0.11484
HardShadow = 0 NotLocked
ShadowSoft = 12.072
Reflection = 0 NotLocked
DebugSun = false
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,-0.6077
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0.6,0.8,1
GradientBackground = 0.8989
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
Iterations = 30
CSphRad = 1
BaseColor = 0.7,0.7,0.7
OrbitStrength = 0.42361
segAColor = 0.666667,0.333333,1
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.705882,0.698039,0.792157
AB = 4
AC = 2
AD = 3
BC = 3
BD = 2
CD = 5
activeMirrors = 1,1,0,0
vertexSize = 0.12
edgeSize = 0.05
#endpreset


#preset 363-camera-at-origin
FOV = 0.71702
Eye = 0,0,0.1
Target = 0,0,1.1
Up = 0,1,0
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -2.90822
DetailAO = -2.33331
FudgeFactor = 1
MaxRaySteps = 255
Dither = 0.55857
NormalBackStep = 0.7143
AO = 0,0,0,1
Specular = 0.23464
SpecularExp = 8.73
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.38602,-0.4995
CamLight = 0.878431,0.921569,0.956863,0.86754
CamLightMin = 0.667
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 254
Fog = 0.1982
HardShadow = 0 NotLocked
ShadowSoft = 12.072
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.658824,0.658824,0.658824
OrbitStrength = 0.77778
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,-0.6077
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0,0,0
GradientBackground = 0.8989
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
segAColor = 0.666667,0.333333,1
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.705882,0.698039,0.792157
AB = 3
AC = 2
AD = 2
BC = 2
BD = 6
CD = 3
activeMirrors = 0,0,0,1
vertexSize = 0.05715
edgeSize = 0.0266
Iterations = 1000
CSphRad = 0.997
#endpreset


#preset 633-0100-inside-near-the-boundary
FOV = 0.71702
Eye = 0.843899,-0.0781583,0.0162983
Target = 1.05239,0.896209,-0.0681697
Up = -0.624998,0.777355,-0.0713888
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -2.77298
DetailAO = -2.33331
FudgeFactor = 1
MaxRaySteps = 255
Dither = 0.55857
NormalBackStep = 0.7143
AO = 0,0,0,1
Specular = 0.23464
SpecularExp = 8.73
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.38602,-0.4995
CamLight = 0.878431,0.921569,0.956863,0.86754
CamLightMin = 0.667
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 254
Fog = 0.11484
HardShadow = 0 NotLocked
ShadowSoft = 12.072
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.7,0.7,0.7
OrbitStrength = 0.42361
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,-0.6077
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0.6,0.8,1
GradientBackground = 0.8989
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
segAColor = 0.666667,0.333333,1
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.705882,0.698039,0.792157
AB = 6
AC = 2
AD = 2
BC = 2
BD = 3
CD = 3
activeMirrors = 0,1,0,0
vertexSize = 0.04
edgeSize = 0.01862
Iterations = 500
CSphRad = 1
#endpreset


#preset 5343-1101-camera-at-origin
FOV = 0.71702
Eye = 0,0,0
Target = -0.230555,0.298189,-0.387205
Up = -0.982041,0.140809,0.125572
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -2.77298
DetailAO = -2.33331
FudgeFactor = 1
MaxRaySteps = 255
Dither = 0.55857
NormalBackStep = 0.7143
AO = 0,0,0,1
Specular = 0.23464
SpecularExp = 8.73
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.38602,-0.4995
CamLight = 0.878431,0.921569,0.956863,0.86754
CamLightMin = 0.667
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 254
Fog = 0.75676
HardShadow = 0 NotLocked
ShadowSoft = 12.072
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.7,0.7,0.7
OrbitStrength = 0.42361
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,0.3923
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0.6,0.8,1
GradientBackground = 0.8989
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
Iterations = 30
CSphRad = 1
segAColor = 0.666667,0.333333,1
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.705882,0.698039,0.792157
AB = 5
AC = 2
AD = 3
BC = 3
BD = 2
CD = 4
activeMirrors = 1,1,0,1
vertexSize = 0.05715
edgeSize = 0.03191
#endpreset


#preset 323532-1001-inside-near-the-boundary
FOV = 0.71702
Eye = 0.813589,-0.41621,-0.212572
Target = 0.837027,0.324841,-0.17552
Up = -0.476474,-0.875695,0.0782962
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -3.11108
DetailAO = -1.28331
FudgeFactor = 1
MaxRaySteps = 255
Dither = 0.55857
NormalBackStep = 0.7143
AO = 0,0,0,1
Specular = 0.3743
SpecularExp = 8.73
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.38236,-0.13236
CamLight = 0.878431,0.921569,0.956863,0.6383
CamLightMin = 0.6087
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 254
Fog = 1.02702
HardShadow = 0 NotLocked
ShadowSoft = 12.072
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.780392,0.780392,0.780392
OrbitStrength = 0
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,0.3923
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0.6,0.8,1
GradientBackground = 0.8989
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
Iterations = 1000
CSphRad = 1
segAColor = 0.666667,0.333333,1
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.76,0.65,0.26
AB = 3
AC = 2
AD = 3
BC = 5
BD = 3
CD = 2
activeMirrors = 1,0,0,1
vertexSize = 0.08285
edgeSize = 0.04096
#endpreset


#preset 535-camera-at-orogin
FOV = 0.71702
Eye = 0,0,0
Target = -0.581912,0.719656,-0.378778
Up = 0.763343,0.643991,0.0508299
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -4.93717
DetailAO = -1.82777
FudgeFactor = 1
MaxRaySteps = 255
Dither = 0.55857
NormalBackStep = 0.7143
AO = 0,0,0,1
Specular = 0.0838
SpecularExp = 20.635
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.48921
SpotLightDir = -0.38236,0.20588
CamLight = 0.878431,0.921569,0.956863,0.6383
CamLightMin = 0.60882
Glow = 0.027451,0.00784314,0.00784314,0.34637
GlowMax = 142
Fog = 0.2072
HardShadow = 0 NotLocked
ShadowSoft = 11.5108
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.529412,0.529412,0.529412
OrbitStrength = 0.48611
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,0.3923
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0.6,0.8,1
GradientBackground = 0.8989
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
segAColor = 0.65098,0.580392,0.258824
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.909804,0.937255,0.976471
AB = 5
AC = 2
AD = 2
BC = 3
BD = 2
CD = 5
activeMirrors = 1,0,0,0
vertexSize = 0.24074
edgeSize = 0.088
Iterations = 325
CSphRad = 0.9992
#endpreset


#preset 424325-1000-limit-set
FOV = 0.71702
Eye = 0.925638,-0.0966573,0.00028089
Target = 0.647421,0.86328,-0.0331159
Up = -0.911385,0.411471,-0.00829091
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -3.11108
DetailAO = -1.28331
FudgeFactor = 1
MaxRaySteps = 255
Dither = 0.55857
NormalBackStep = 0.7143
AO = 0,0,0,1
Specular = 0.3743
SpecularExp = 8.73
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.38236,-0.13236
CamLight = 0.878431,0.921569,0.956863,0.6383
CamLightMin = 0.6087
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 254
Fog = 1.02702
HardShadow = 0 NotLocked
ShadowSoft = 12.072
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.780392,0.780392,0.780392
OrbitStrength = 0
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,0.3923
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
BackgroundColor = 0.6,0.8,1
GradientBackground = 0.8989
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
segAColor = 0.666667,0.333333,1
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.76,0.65,0.26
AB = 4
AC = 2
AD = 4
BC = 3
BD = 2
CD = 5
activeMirrors = 1,0,0,0
vertexSize = 0.08285
edgeSize = 0.04096
Iterations = 1000
CSphRad = 1
#endpreset


#preset 444-1110-upper-half-space-view
doUpperHalfSpace = true
FOV = 0.71702
Eye = 1.33725,-0.0912647,0.400075
Target = -0.298632,-0.320828,-0.318814
Up = 0,0,1
EquiRectangular = false
FocalPlane = 1
Aperture = 0
Gamma = 1.1579
ToneMapping = 5
Exposure = 1.30146
Brightness = 0.9175
Contrast = 0.52505
Saturation = 0.14565
GaussianWeight = 1
AntiAliasScale = 2
Detail = -3.85504
DetailAO = -1.59446
FudgeFactor = 1
MaxRaySteps = 709
Dither = 0.84762
NormalBackStep = 3.0357
AO = 0,0,0,1
Specular = 0.3743
SpecularExp = 8.73
SpecularMax = 6.061
SpotLight = 0.772549,0.85098,0.94902,0.5253
SpotLightDir = -0.22058,-0.25
CamLight = 0.878431,0.921569,0.956863,0.66666
CamLightMin = 0.6087
Glow = 0.027451,0.00784314,0.00784314,0.6604
GlowMax = 254
Fog = 0.55856
HardShadow = 0 NotLocked
ShadowSoft = 12.072
Reflection = 0 NotLocked
DebugSun = false
BaseColor = 0.835294,0.835294,0.835294
OrbitStrength = 0
X = 0.0627451,0.0784314,0.0784314,0.69038
Y = 0.72549,0.85098,1,0.3923
Z = 0.8,0.78,1,-0.50384
R = 0.4,0.7,1,0.46872
GradientBackground = 0.8989
CycleColors = false
Cycles = 0.65577
EnableFloor = false
FloorNormal = 0,0,1
FloorHeight = 0
FloorColor = 1,1,1
Iterations = 1000
BackgroundColor = 0.6,0.8,1
CSphRad = 1
segAColor = 0.666667,0.333333,1
segBColor = 0.545098,0.737255,0.72549
segCColor = 0.647059,0.866667,0.843137
segDColor = 0.8,0.74902,0.847059
verticesColor = 0.76,0.65,0.26
AB = 4
AC = 2
AD = 2
BC = 2
BD = 4
CD = 4
activeMirrors = 1,1,0,1
vertexSize = 0.08285
edgeSize = 0.04096
#endpreset
