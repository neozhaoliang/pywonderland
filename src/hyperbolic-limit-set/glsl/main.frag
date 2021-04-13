#version 130
/*
=============================================

Limit set of rank 4 hyperbolic Coxeter groups

                                by Zhao Liang
=============================================

This program shows the limit set of rank 4 hyperbolic Coxeter groups.
Dont't be scared by the title, it's a rather simple program, the scene
contains only one sphere and one plane :P.

Some math stuff:

Let G be a hyperbolic Coxeter group and x a point inside the hyperbolic
unit ball, the orbit S_x = { gx, g \in G } has accumulation points
(under Euclidean metric) only on the boundary of the space. We call the
accumulation points of S_x the limit set of the group, it can be proved that
this set is independent of the way x is chosen, and it's the smallest
closed subset of the boundary that is invariant under the action of the group.

The Coxeter-Dynkin diagram of a rank 4 Coxeter group of string type has the form

   A --- B --- C --- D
      p     q     r

Here A, B, D can be chosen as ususal Euclidean planes, C is a sphere orthongonal
to the unit ball. This is taken from mla's notation, and as far as I know this
has long been used by users on fractalforums. (fragmentarium)

In this animation these points are colored in "brass metal".

==========
!important
==========

The limit set is a closed set with no interior points, to show them we have
to use an approximate procedure: we simply try to reflect a point p on the
boundary to the fundamental domain up to a maximum steps, once failed then we
think p belongs to the limit set.

**So the number MAX_REFLECTIONS is an important param**, if' its set to a high
threshold then little limit set will be shown, or if it's not high enough then
the boundary of the set will look too coarse, so beware of this.

As always, you can do whatever you want to this work.

Update: thanks @mla for helping fix some bugs!
*/
// ------------------------------------------

// want to add some shiny texture effect to the limit set?
#define TEXBUMP  0.007

// --------------------------
// You can try more patterns like
// (3, 7, 3), (4, 6, 3), (4, 4, 5), (5, 4, 4), (7, 3, 4), ..., etc. (5, 4, 4) is now
// my favorite! set PQR below to see the result.
// For large PQRs the limit set will become too small to be visible, you need to adjust
// MAX_REFLECTIONS and tweak with the function chooseColor to get appealling results.

uniform vec4 iMouse;
uniform float iTime;
uniform vec3 iResolution;
uniform vec3 PQR;
uniform sampler2D iChannel0;

out vec4 finalColor;

// --------------------------
// some global settings

#define MAX_TRACE_STEPS  100
#define MIN_TRACE_DIST   0.1
#define MAX_TRACE_DIST   100.0
#define PRECISION        0.0001
#define AA               3
#define MAX_REFLECTIONS  500
#define PI               3.141592653

// another pattern
#define CHECKER1  vec3(0.196078, 0.33, 0.82)
#define CHECKER2  vec3(0.75, 0.35, 0.196078)

//#define CHECKER1  vec3(0.82, 0.196078, 0.33)
//#define CHECKER2  vec3(0.196078, 0.35, 0.92)
#define MATERIAL  vec3(0.71, 0.65, 0.26)
#define FUNDCOL   vec3(0., 0.82, .33)

// used to highlight the limit set
#define LighteningFactor 8.
// --------------------------

vec3 A, B, D;
vec4 C;
float orb;

// minimal distance to the four mirrors
float distABCD(vec3 p)
{
    float dA = abs(dot(p, A));
    float dB = abs(dot(p, B));
    float dD = abs(dot(p, D));
    float dC = abs(length(p - C.xyz) - C.w);
    return min(dA, min(dB, min(dC, dD)));
}

// try to reflect across a plane with normal n and update the counter
bool try_reflect(inout vec3 p, vec3 n, inout int count)
{
    float k = dot(p, n);
    // if we are already inside, do nothing and return true
    if (k >= 0.0)
    	return true;

    p -= 2.0 * k * n;
    count += 1;
    return false;
}

// similar with above, instead this is a sphere inversion
bool try_reflect(inout vec3 p, vec4 sphere, inout int count)
{
    vec3 cen = sphere.xyz;
    float r = sphere.w;
    vec3 q = p - cen;
    float d2 = dot(q, q);
    if (d2 == 0.0)
    	return true;
    float k = (r * r) / d2;
    if (k < 1.0)
    	return true;
    p = k * q + cen;
    count += 1;
    orb *= k;
    return false;
}

// sdf of the unit sphere at origin
float sdSphere(vec3 p, float radius) { return length(p) - 1.0; }

// sdf of the plane y=-1
float sdPlane(vec3 p, float offset) { return p.y + 1.0; }

// inverse stereo-graphic projection, from a point on plane y=-1 to
// the unit ball centered at the origin
vec3 planeToSphere(vec2 p)
{
    float pp = dot(p, p);
    return vec3(2.0 * p, pp - 1.0).xzy / (1.0 + pp);
}

// iteratively reflect a point on the unit sphere into the fundamental cell
// and update the counter along the way
bool iterateSpherePoint(inout vec3 p, inout int count)
{
    bool inA, inB, inC, inD;
    for(int iter=0; iter<MAX_REFLECTIONS; iter++)
    {
        inA = try_reflect(p, A, count);
        inB = try_reflect(p, B, count);
        inC = try_reflect(p, C, count);
        inD = try_reflect(p, D, count);
        p =  normalize(p);  // avoid floating error accumulation
        if (inA && inB && inC && inD)
            return true;
    }
    return false;
}

// colors for fundamental domain, checker pattern and limit set.
vec3 chooseColor(bool found, int count)
{
    vec3 col;
    if (found)
    {
        if (count == 0) return FUNDCOL;
        else if (count >= 300) col = MATERIAL;
        else
            col = (count % 2 == 0) ? CHECKER1 : CHECKER2;

    }
    else
        col = MATERIAL;

    float t =  float(count) / float(MAX_REFLECTIONS);
    col = mix(MATERIAL*LighteningFactor, col, 1. - t * smoothstep(0., 1., log(orb) / 32.));
    return col;
}

// 2d rotation
vec2 rot2d(vec2 p, float a) { return p * cos(a) + vec2(-p.y, p.x) * sin(a); }

vec2 map(vec3 p)
{
    float d1 = sdSphere(p, 1.0);
    float d2 = sdPlane(p, -1.0);
    float id = (d1 < d2) ? 0.: 1.;
    return vec2(min(d1, d2), id);
}

// standard scene normal
vec3 getNormal(vec3 p)
{
    const vec2 e = vec2(0.001, 0.);
    return normalize(
        vec3(
            map(p + e.xyy).x - map(p  - e.xyy).x,
            map(p + e.yxy).x - map(p  - e.yxy).x,
            map(p + e.yyx).x - map(p  - e.yyx).x
            )
        );
}

// get the signed distance to an object and object id
vec2 raymarch(in vec3 ro, in vec3 rd)
{
    float t = MIN_TRACE_DIST;
    vec2 h;
    for(int i=0; i<MAX_TRACE_STEPS; i++)
    {
        h = map(ro + t * rd);
        if (h.x < PRECISION * t)
            return vec2(t, h.y);

        if (t > MAX_TRACE_DIST)
            break;

        t += h.x;
    }
    return vec2(-1.0);
}

float calcOcclusion(vec3 p, vec3 n) {
    float occ = 0.0;
    float sca = 1.0;
    for (int i = 0; i < 5; i++) {
        float h = 0.01 + 0.15 * float(i) / 4.0;
        float d = map(p + h * n).x;
        occ += (h - d) * sca;
        sca *= 0.75;
    }
    return clamp(1.0 - occ, 0.0, 1.0);
}


float softShadow(vec3 ro, vec3 rd, float tmin, float tmax, float k) {
    float res = 1.0;
    float t = tmin;
    for (int i = 0; i < 12; i++) {
        float h = map(ro + rd * t).x;
        res = min(res, k * h / t);
        t += clamp(h, 0.01, 0.2);
        if (h < 0.0001 || t > tmax)
            break;
    }
    return clamp(res, 0.0, 1.0);
}

// shane's tex3D function
vec3 tex3D(sampler2D t, in vec3 p, in vec3 n)
{
    n = max(abs(n) - .02, .001);
    n /= length(n);
    vec3 tx = texture(t, p.yz).xyz;
    vec3 ty = texture(t, p.zx).xyz;
    vec3 tz = texture(t, p.xy).xyz;
    return (tx*tx*n.x + ty*ty*n.y + tz*tz*n.z);
}

vec3 texBump( sampler2D tx, in vec3 p, in vec3 n, float bf)
{
    const vec2 e = vec2(.001, 0);
    mat3 m = mat3(tex3D(tx, p - e.xyy, n), tex3D(tx, p - e.yxy, n), tex3D(tx, p - e.yyx, n));
    vec3 g = vec3(.299, .587, .114)*m;
    g = (g - dot(tex3D(tx,  p , n), vec3(.299, .587, .114)))/e.x;
    g -= n*dot(n, g);
    return normalize( n + g*bf );
}

vec3 getColor(vec3 ro, vec3 rd, vec3 pos, vec3 nor, vec3 lp, vec3 basecol)
{
    vec3 col = vec3(0.0);
    vec3 ld = lp - pos;
    float lDist = max(length(ld), .001);
    ld /= lDist;
    float ao = calcOcclusion(pos, nor);
    float sh = softShadow(pos+0.001*nor, ld, 0.02, lDist, 32.);
    float diff = clamp(dot(nor, ld), 0., 1.);
    float atten = 2. / (1. + lDist * lDist * .01);

    float spec = pow(max( dot( reflect(-ld, nor), -rd ), 0.0 ), 32.);
    float fres = clamp(1.0 + dot(rd, nor), 0.0, 1.0);

    col += basecol * diff;
    col += basecol * vec3(1., 0.8, 0.3) * spec * 4.;
    col += basecol * vec3(0.8) * fres * fres * 2.;
    col *= ao * atten * sh;
    col += basecol * clamp(0.8 + 0.2 * nor.y, 0., 1.) * 0.5;
    return col;
}

mat3 sphMat(float theta, float phi)
{
    float cx = cos(theta);
    float cy = cos(phi);
    float sx = sin(theta);
    float sy = sin(phi);
    return mat3(cy, -sy * -sx, -sy * cx,
                0,   cx,  sx,
                sy,  cy * -sx, cy * cx);
}


void main()
{
    vec2 fragCoord = gl_FragCoord.xy;
    vec3 finalcol = vec3(0.);
    int count = 0;
    vec2 m = vec2(0.0, 1.0) + iMouse.xy / iResolution.xy;
    float rx = m.y * PI;
    float ry = -m.x * 2. * PI;
    mat3 mouRot = sphMat(rx, ry);

// ---------------------------------
// initialize the mirrors

    float P = PQR.x, Q = PQR.y, R = PQR.z;
    float cp = cos(PI / P), sp = sin(PI / P);
    float cq = cos(PI / Q);
    float cr = cos(PI / R);
    A = vec3(0,  0,   1);
    B = vec3(0, sp, -cp);
    D = vec3(1,  0,   0);

    float r = 1.0 / cr;
    float k = r * cq / sp;
    vec3 cen = vec3(1, k, 0);
    C = vec4(cen, r) / sqrt(dot(cen, cen) - r * r);

// -------------------------------------
// view setttings

    vec3 camera = vec3(3., 3.2, -3.);
    vec3 lp = camera + vec3(0.5, 1.0, -0.3); //light position
    camera.xz = rot2d(camera.xz, iTime*0.3);
    vec3 lookat  = vec3(0.);
    vec3 up = vec3(0., 1., 0.);
    vec3 forward = normalize(lookat - camera);
    vec3 right = normalize(cross(forward, up));
    up = normalize(cross(right, forward));

// -------------------------------------
// antialiasing loop

    for(int ii=0; ii<AA; ii++)
    {
        for(int jj=0; jj<AA; jj++)
        {
            vec2 o = vec2(float(ii), float(jj)) / float(AA);
            vec2 uv = (2. * fragCoord + o - iResolution.xy) / iResolution.y;
            vec3 rd = normalize(uv.x * right + uv.y * up + 2.0 * forward);
            orb = 1.0;
            // ---------------------------------
            // hit the scene and get distance, object id

            vec2 res = raymarch(camera, rd);
            float t = res.x;
            float id = res.y;
            vec3 pos = camera + t * rd;

            bool found;
            float edist;
            vec3 col;
            // the sphere is hit
            if (id == 0.)
            {
                vec3 nor = pos;
                vec3 q = pos * mouRot;
                found = iterateSpherePoint(q, count);
                edist = distABCD(q);
                vec3 basecol = chooseColor(found, count);
#ifdef TEXBUMP
                if (!found)
                    nor = texBump(iChannel0, pos, nor, TEXBUMP);
#endif
                col = getColor(camera, rd, pos, nor, lp, basecol);
            }
            // the plane is hit
            else if (id == 1.)
            {
                vec3 nor = vec3(0., 1., 0.);
                vec3 q = planeToSphere(pos.xz);
                q = q * mouRot;
                found = iterateSpherePoint(q, count);
#ifdef TEXBUMP
                 if (!found)
                    nor = texBump(iChannel0, pos, nor, TEXBUMP);
#endif
                edist = distABCD(q);
                vec3 basecol = chooseColor(found, count);
                col = getColor(camera, rd, pos, nor, lp, basecol) * .9;
            }
            // draw the arcs
            col = mix(col, vec3(0.), (1.0 - smoothstep(0., 0.005, edist))*0.85);
            col = mix(col, vec3(0.), 1.0 - exp(-0.01*t*t));
            finalcol += col;
        }
    }
    finalcol /= (float(AA) * float(AA));

// ------------------------------------
// a little post-processing

    finalcol = mix(finalcol, 1. - exp(-finalcol), .35);
    finalColor = vec4(sqrt(max(finalcol, 0.0)), 1.0);
}
