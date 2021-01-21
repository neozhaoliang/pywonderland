#version 130

uniform vec3 iResolution;
uniform float iTime;

out vec4 FinalColor;


/*
====================================================

Apeiodic tiling using de Bruijn's algebraic approach

                                       by Zhao Liang
====================================================

This shader is motivated by Greg Egan's javascript applet at

    http://gregegan.net/APPLETS/02/02.html

Thanks Egan for explaining his idea to me! (and the comments in his code :)

Also I learned a lot from Shane's wonderful examples.

You can do whatever you want to this program.

Below I'll give a brief sketch of the procedure used in this program,
for a detailed explanation please refer to

"Algebraic theory of Penrose's non-periodic tilings of the plane".
                                                   N.G. de Bruijn.

Also I found the book

"Aperiodic Order, Volume 1", by Baake M., Grimm U., Penrose R.

very helpful.

Main steps: (use N=5 as example)

1. We choose the five fifth roots of unity as grid directions.
   Each direction will have a family of grid lines orthogonal to it and
   has unit spacing between adjacent lines.

2. We also choose five reals to shift each grid along its direction.

3. Any intersection point P of two grid lines can be identified with four integers
   (r, s, kr, ks), which means P is the intersection of the kr-th line in the r-th
   grid and the ks-th line in the s-th grid. It must hold 0 <= r < s < 5.

4. Each intersection point P correspondes to an unique rhombus in the final tiling. Note
   this rhombus does not necessarily contain P but a transformed version of P.

5. For each pixel uv, we do a bit lengthy computation to find which rhombus its
   transformed position lies in.

6. Color the rhombus acoording to its shape, the position, ... whatever you want.

7. We also draw a tunnel in each face and flip the tunnel randomly to make some cubes
   look impossible. (a cube is formed by three rhombus meeting at an obtuse vertex)
   Note this is different from Egan's applet, in there he carefully chose fixed flips
   for each rhombus to make **every** cube look impossible. Our random flips here only
   make **some** cubes look impossible.

All suggestions are welcomed.
*/

// if you want some faces are closed and draw a cross bar on them
#define SOME_CLOSED_FACES

// dimension of the grids
const int N = 5;

// N real numbers for the shifts of the grids.
float[N] shifts;

// directions of the grids, will be initialized in the beginning of the main function
vec2[N] grids;

struct Rhombus
{
    // r, s for the r-th and s-th grids.
    int r;
    int s;

    // kr, ks for the lines in the two grids
    float kr;
    float ks;

    // center and vertices of the rhombus
    vec2 cen;
    vec2[4] verts;

    // the vertices of the tunnels. Each tunnel contains two pieces.
    vec2[4] inset1;
    vec2[4] inset2;
};

#define PI 3.141592653

// init the grid directions, we choose the five fifth roots of unity
void init_grids()
{
    float theta;
    for(int k=0; k<N; k++)
    {
        theta = (N % 2 == 0) ? PI / float(N) * float(k) : 2. * PI / float(N) * float(k);
        grids[k] = vec2(cos(theta), sin(theta));
        // for N=5 (0.2, 0.2, 0.2, 0.2, 0.2) gives the usual Penrose tiling.
        // set all shifts to 0.5 will give the star pattern which contains 10 thin thombus
        // around a vertex hence is non-Penrose.
        // shifts[k] = 0.5;
        shifts[k] = 1. / float(N);
    }
}

// 2d cross product of two vectors. It's just the determinant of the 2x2 matrix
// formed by (p, q). This is useful when we want to solve t for points p, q, v
// so that p+t*q is parellel to v. Just take
// ccross(p+tq, v) = 0 --> t = -ccross(p, v) / ccross(q, v)
float ccross(vec2 p, vec2 q) { return p.x * q.y - p.y * q.x; }

// iq's hash function, for randomly flip the tunnels and open/closed faces
float hash21(vec2 p) { return fract(sin(dot(p, vec2(141.13, 289.97))) * 43758.5453); }

// distance from a 2d point p to a 2d segment (a, b)
float dseg(vec2 p, vec2 a, vec2 b)
{
	vec2 v = b - a;
    p -= a;
    float t = clamp(dot(p, v)/ dot(v, v), 0., 1.);
    return length(p - t * v);
}

// check if a point p is in the convex cone C = { s*a+t*b | s,t >= 0 }.
// we assume a, b are not parallel: ccross(a, b) != 0.
// again we use cross product to do this.
bool incone(vec2 p, vec2 a, vec2 b)
{
    float cpa = ccross(p, a);
    float cpb = ccross(p, b);
    float cab = ccross(a, b);
    float s = -cpa / cab, t = cpb / cab;
    return (s >= 0.) && (t >= 0.);
}

// check if a 2d point p is inside a convex quad with vertices stored in an
// array of four 2d vectors. Here we assume the vertices are aranged in order:
// A--B--C--D, either clockwise or anti-clockwise.
// we simple check if p-A is in the cone (B-A, D-A) and p-C is in the cone (B-C, D-C).
bool inquad(vec2 p, vec2[4] verts)
{
    vec2 q = p - verts[0];
    vec2 a = verts[1] - verts[0];
    vec2 b = verts[3] - verts[0];
    bool inab = incone(q, a, b);

    if (!inab) return false;

    q = p - verts[2];
    a = verts[1] - verts[2];
    b = verts[3] - verts[2];
    inab = incone(q, a, b);
    return inab;
}

// distance function from a 2d point p to a rhombus.
// this is a signed distance version, points inside will return negative distances.
float dquad(vec2 p, vec2[4] verts)
{
    float dmin = dseg(p, verts[0], verts[1]);
    dmin = min(dmin, dseg(p, verts[1],  verts[2]));
    dmin = min(dmin, dseg(p, verts[2],  verts[3]));
    dmin = min(dmin, dseg(p, verts[3],  verts[0]));
    return inquad(p, verts) ? -dmin : dmin;
}

// project a vector p to the k-th grid, note each grid line is shifted so we need
// to add the corresponding shifts.
float project_point_grid(vec2 p, int k) { return dot(p, grids[k]) + shifts[k]; }

// for a point p and for each 0 <= k < 5, p must lie between the (m, m+1)-th lines in
// the k-th grid for some integer m. we use a bool param `lower` to choose return m or m+1.
float[N] get_point_index(in vec2 p, bool lower)
{
    float[N] index;
    for(int k=0; k<N; k++)
    {
        float offset = project_point_grid(p, k);
        index[k] = lower ? floor(offset) : ceil(offset);
    }
    return index;
}

// find the vertices of the rhombus corresponding to the intersection point P,
// where P is the intersection of the kr-th line and ks-th line in the r/s grids.
void solve_rhombus_verts(int r, int s, float kr, float ks, out vec2[4] verts)
{
    vec2 P = grids[r] * (ks - shifts[s]) - grids[s] * (kr - shifts[r]);
    P = vec2(-P.y, P.x) / grids[s - r].y;
    float[N] index = get_point_index(P, false);
    index[r] = kr; index[s] = ks;
    vec2 sum = vec2(0.0);
    for(int k=0; k<N; k++)
    {
        sum += grids[k] * index[k];
    }
    verts[0] = sum;
    verts[1] = sum + grids[r];
    verts[3] = sum + grids[s];
    verts[2] = verts[1] + grids[s];
}

// this is the "continous" version of de Bruijn's transformation that maps a pixel
// to its position in the tiling.
vec2 debruijn_transform(vec2 p)
{
    vec2 sum = vec2(0.0);
    for(int k=0; k<N; k++)
    {
        sum += grids[k] * project_point_grid(p, k);
    }
    return sum;
}

// a bit lengthy computation to find after the transformation p --> q,
// which rhombus q lies in. we simply iterate over all possible combinations:
// for each pair 0 <= r < s < 5, we find (kr, ks) so that p lies in the (kr, kr+1)
// strip in the r-th grid and (ks, ks+1) strip in the s-th grid, and check which of
// the four rhombus (r, s, kr, ks), (r, s, kr, ks+1), (r, s, kr+1, ks), (r, s, kr+1, ks+1)
// contains q.
// Sadly due to float rounding errors, we have to search from (r, s, kr-1, ks-1).
Rhombus get_mapped_rhombus(vec2 p, out vec2 q)
{
    q = debruijn_transform(p);
    float[N] pindex = get_point_index(p, true);
    Rhombus rb;
    float kr, ks;
    vec2[4] verts;
    for(int r=0; r<N-1; r++)
    {
        for(int s=r+1; s<N; s++)
        {
            for(float dr=-1.; dr<2.; dr+=1.0)
            {
                for(float ds=-1.; ds<dr+2.; ds+=1.0)
                {
                    kr = pindex[r] + dr;
                    ks = pindex[s] + ds;
                    solve_rhombus_verts(r, s, kr, ks, verts);
                    if (inquad(q, verts))
                    {
                        rb.r = r, rb.s = s, rb.kr = kr, rb.ks = ks;
                        rb.verts = verts;
                        rb.cen = (verts[0] + verts[1] + verts[2] + verts[3]) / 4.0;
                        return rb;
                    }
                }
            }
        }
    }
}

// For each tunnel in the face, we want it to slant by a best-looking direction.
// We simply choose a grid line direction that matches best with the diagonal line
// of this face. This is proposed by Greg Egan.
vec2 get_best_dir(int r, int s, vec2 v)
{
    float maxdot = 0.;
    float inn = 0.;
    vec2 result;
    for(int m=0; m<N; m++)
    {
        if ((m != r) && (m != s))
        {
            inn = dot(grids[m], v);
            if (abs(inn) > maxdot)
            {
                maxdot = abs(inn);
                result = (inn > 0.) ? grids[m] : -grids[m];
            }
        }
    }
    return result;
}

// Compute the vertices of the two pieces of the tunnel
void get_tunnels(inout Rhombus rb)
{
    vec2 gr = grids[rb.r] / 2.;
    vec2 gs = grids[rb.s] / 2.;
    float cA = dot(gr, gs);
    float sgn = sign(cA);
    if (sgn == 0.0) sgn = sign(hash21(rb.cen) - 0.5);
    vec2 xy = (-gr + sgn * gs) / 2.;
    vec2 XY = get_best_dir(rb.r, rb.s, xy);

    XY /= 7.0;

    // the first piece
    rb.inset1[0] = (gr - sgn * gs) / 2.;
    rb.inset1[1] = rb.inset1[0] + XY;
    rb.inset1[3] = (sgn * gr + gs) / 2.;
    vec2 v1 = rb.inset1[0] + rb.inset1[3];
    vec2 v2 = rb.inset1[3] - rb.inset1[0];
    float t = ccross(XY, v2) / ccross(v1,  v2);
    rb.inset1[2] =  rb.inset1[3] + t * v1;
    // the other piece. it shares two vertices with the first one.
    rb.inset2[0] =  rb.inset1[0];
    rb.inset2[1] =  rb.inset1[1];
    rb.inset2[3] = -rb.inset1[3];

    v1 = rb.inset2[0] + rb.inset2[3];
    v2 = rb.inset2[3] - rb.inset2[0];
    t = ccross(XY, v2) / ccross(v1,  v2);
    rb.inset2[2] = rb.inset2[3] + t * v1;
}

float getCross(vec2 p, Rhombus rb)
{
    vec2 vA = (rb.verts[0] + rb.cen) / 2.;
    vec2 vB = (rb.verts[1] + rb.cen) / 2.;
    vec2 vC = (rb.verts[2] + rb.cen) / 2.;
    vec2 vD = (rb.verts[3] + rb.cen) / 2.;
    float dcross = dseg(p, vA, vB);
    dcross = min(dcross, dseg(p, vB, vC));
    dcross = min(dcross, dseg(p, vC, vD));
    dcross = min(dcross, dseg(p, vD, vA));
    dcross = min(dcross, dseg(p, vA, vC));
    dcross = min(dcross, dseg(p, vB, vD));
    return dcross;
}


void main()
{
    vec2 uv = gl_FragCoord.xy / iResolution.xy - 0.5;
    uv.y *= iResolution.y / iResolution.x;
    // you can control this "zoom" factor here, a larger factor will give a
    // more dense view.
    uv *= 6.;

    float sf = 0.01;
    
    // initialize our grids
    init_grids();

    // p is transformed position of uv, vary its position by translating along
    // a fixed direction.
    vec2 p;
    Rhombus rb = get_mapped_rhombus(uv + iTime, p);
    get_tunnels(rb);

    // relative position of the transformed position with respect to rhombus center
    vec2 q = p - rb.cen;

    // assign a random number to each face, we let this random number vary by time
    // so the face can also vary its tunnel directions, openness, etc.
    float rnd = hash21(rb.cen);
    rnd = sin(rnd * 6.283 + iTime) * .5 + .5;

    // changed to Shane's color scheme
    float blink = smoothstep(0., .125, rnd - .15);
    vec3 col = .5 + .45*cos(6.2831*rnd + vec3(0., 1., 2.) - .25);
    vec3 col2 = .5 + .45*cos(6.2831*dot(rb.cen, vec2(1.)) + vec3(2., 3., 1.) - .25);
    col = mix(col, pow(col*col2, vec3(.65))*2., .25); 
    col = mix(col, col2.xzy,  float(rb.r * rb.s) / float(N*N*2)*blink);

    // cA and sA are the cos/sin of the angle at vertice A
    float cA = dot(grids[rb.r], grids[rb.s]);
    float sA = sqrt(1. - cA * cA);

    float dcen = dot(q, q) * 1.5;

    if(rnd > .2)
    {
        q.xy = -q.xy; // randomly flip the tunnels to make some cubes look impossible
        col *= min(1.45 - dcen, .75);
    }
    else { col *= min(dcen + 0.75, .9); }

    // distance to the boundary of the face
    float dface = dquad(p, rb.verts);

    // distance to the face border
    float dborder = max(dface, -(dface + 0.006));

    // 5 to the tunnel of the face
    float dtunnel = min(dquad(q, rb.inset1), dquad(q, rb.inset2));

    // distance to the hole of the face,
    // we choose the size of the hole to half the width/height of the rhombus.
    // note each rhombus has unit side length, so sA is twice the distance
    // from the center to its four edges.
    float dhole = dface + sA / 4.0;
    float dcross = 1e5;
    

#ifdef SOME_CLOSED_FACES
    // really dirty, maybe should put into a function
    if(abs(rnd - 0.5) > .48)
    {
        dhole += 1e5; dtunnel += 1e5;
        dcross = min(dcross, getCross(p, rb));
    }
#endif

    // shade the tunnels by the type of the rhombus
    float shade;

    float id = floor(hash21(vec2(float(rb.r), float(rb.s))) * 3.);

    // qd is our shading direction
    int ind = cA >= 0. ? 0 : 1;
    float qd = dot(q, rb.cen - rb.verts[ind]);
    if(id == 0.)
        shade = .8 -  step(0., -sign(rnd - .5)*qd) * .3;
    else if(id == 1.)
        shade = .6 -  step(0., -sign(rnd - .5)*qd) * .4;
    else
        shade = .7 -  step(0., -sign(rnd - .5)*qd) * .4;

    
    // draw the black hole
    col = mix(col, vec3(0.), (1. - smoothstep(0., sf, dhole)));

    // draw the face border
    col = mix(col, vec3(0.), (1. - smoothstep(0., sf*2., dborder)) * .95);

    // shade the tunnels
    col = mix(col, vec3(1.), (1. - smoothstep(0., sf, dtunnel)) * shade);

    // highlight the edges
    col = mix(col, col * 2., (1. - smoothstep(0., sf*2., dborder-sf*2.)) * .3);

    // draw the crosses on solid faces
    col = mix(col, vec3(0.), (1. - smoothstep(0., sf, dcross-sf/2.)) * .5);

    // adjust luminance of faces by their types
    col *= min(id / 2. + .5, 1.25);

    // draw hatch lines on the face to add some decorate pattern.
    // we get line direction first
    vec2 diag = (rb.verts[0] - rb.cen);
    float dd = cA < 0. ? dot(q, diag) : dot(q, vec2(-diag.y, diag.x));
    float hatch = clamp(sin(dd * 60. * PI) * 2. + .5, 0., 1.);
    float hrnd = hash21(floor(q * 400. * PI) + 0.73);
    if (hrnd > 0.66) hatch = hrnd;

    // we dont't want the hatch lines to show on top of the hole and tunnel
    if (dtunnel < 0.0 || dhole < 0.0) hatch = 1.0;
    col *= hatch *.1 + .85;

    // add a thin bounding box around the hole
    col = mix(col, vec3(0.), (1. - smoothstep(0., sf*1.5, abs(dface + sA/8.)))*.5);
    uv = gl_FragCoord.xy / iResolution.xy;
    col *= pow(16. * uv.x * uv.y * (1. - uv.x) * (1. - uv.y), .125) * .75 + .25;
    FinalColor = vec4(sqrt(max(col, 0.0)), 1.0);
}
