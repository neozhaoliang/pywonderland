/*
Aperiodic tiling using de Bruijn's algebraic approach, Zhao Liang.

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
   kr and ks can be any pair of integers.

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

// If you want some cube faces are closed and draw a cross bar on them
#define SOME_CLOSED_FACES

// dimension of the grids, N=5 is the (generalized) Penrose pattern
const int N = 5;

// control hole size
const float hs = 3.33;

// N real numbers for the shifts of the grids.
float[N] shifts;

// directions of the grids, will be initialized later
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

    // vertices of the tunnels, each tunnel contains two pieces.
    vec2[4] inset1;
    vec2[4] inset2;
};

#define PI 3.141592653

// initialize the grid directions, for N = 5 they are the five fifth roots of unity
void init_grids()
{
    float FN = float(N), theta;
    for(int k = 0; k < N; k++)
    {
        theta = (N % 2 == 0) ? PI / FN * float(k) : PI / FN * float(k) * 2.;
        grids[k] = vec2(cos(theta), sin(theta));
        // for N=5 (0.2, 0.2, 0.2, 0.2, 0.2) gives the classical Penrose tiling.
        // set all shifts to 0.5 will give the star pattern which has ten thin rhombus
        // around a vertex hence is non-Penrose.
        // shifts[k] = 0.5;
        shifts[k] = 1./FN;
    }
}

// distance from a 2d point p to a 2d segment (a, b)
float dseg(vec2 p, vec2 a, vec2 b) {
vec2 v = b - a;
    p -= a;
    float t = clamp(dot(p, v)/dot(v, v), 0., 1.);
    return length(p - t * v);
}

// iq's hash function, for randomly flip the tunnels and open/closed faces
float hash21(vec2 p) {
    return fract(sin(dot(p, vec2(141.13, 289.97))) * 43758.5453);
}

float cross_prod(vec2 p, vec2 q) {
    return p.x * q.y - p.y * q.x;
}

// signed distance function to a polygon using winding number
float sdPoly4(in vec2 p, in vec2[4] verts) {
    float d = dot(p - verts[0], p - verts[0]);
    float s = 1.0;
    for(int i = 0, j = 3; i < 4; j = i, i++) {
        vec2 e = verts[j] - verts[i];
        vec2 w = p - verts[i];
        vec2 b = w - e*clamp(dot(w, e)/dot(e, e), 0., 1.);
        d = min(d, dot(b, b));

        bvec3 cond = bvec3(p.y >= verts[i].y, p.y < verts[j].y, cross_prod(e, w) > 0.);
        if (all(cond) || all(not(cond)))
            s *= -1.0;
    }
    return s * sqrt(d);
}

// project a vector p to the k-th grid, note each grid line is shifted so we need
// to add the corresponding shifts.
float project_point_grid(vec2 p, int k) {
    return dot(p, grids[k]) + shifts[k];
}

// find the vertices of the rhombus corresponding to the intersection point P,
// where P is the intersection of the kr-th line and ks-th line in the r/s grids.
void solve_rhombus_verts(int r, int s, float kr, float ks, out vec2[4] verts) {
    vec2 P = grids[r] * (ks - shifts[s]) - grids[s] * (kr - shifts[r]);
    P = vec2(-P.y, P.x) / grids[s - r].y;
    vec2 sum = kr * grids[r] + ks * grids[s];
    for(int k = 0; k < N; k++) {
        if ((k != r) && (k != s))
            sum += grids[k] * ceil(project_point_grid(P, k));
    }
    verts[0] = sum;
    verts[1] = sum + grids[r];
    verts[3] = sum + grids[s];
    verts[2] = verts[1] + grids[s];
}

// this is the "continous" version of de Bruijn's transformation that maps a pixel
// to its position in the tiling.
vec2 debruijn_transform(vec2 p) {
    vec2 sum = vec2(0.0);
    for(int k = 0; k < N; k++)
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
Rhombus get_mapped_rhombus(vec2 p, out vec2 q) {
    q = debruijn_transform(p);
    Rhombus rb;
    float kr, ks;
    vec2[4] verts;
    float[N] pindex;
    for (int i = 0; i < N; i++) {
        pindex[i] = floor(project_point_grid(p, i));
    }
    for(int r = 0; r < N-1; r++) {
        for(int s = r+1; s < N; s++) {
            for(float dr = -1.; dr < 2.; dr += 1.0) {
                for(float ds = -1.; ds < dr+2.; ds += 1.0) {
                    kr = pindex[r] + dr;
                    ks = pindex[s] + ds;
                    solve_rhombus_verts(r, s, kr, ks, verts);
                    if (sdPoly4(q, verts) < 0.) {
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
vec2 get_best_dir(int r, int s, vec2 v) {
    float maxdot = 0.;
    float inn = 0.;
    vec2 result;
    for(int k = 0; k < N; k++) {
        if ((k != r) && (k != s)) {
            inn = dot(grids[k], v);
            if (abs(inn) > maxdot) {
                maxdot = abs(inn);
                result = (inn > 0.) ? grids[k] : -grids[k];
            }
        }
    }
    return result;
}

// Compute the vertices of the two pieces of the tunnel
void get_tunnels(inout Rhombus rb) {
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
    float t = cross_prod(XY, v2) / cross_prod(v1, v2);
    rb.inset1[2] =  rb.inset1[3] + t * v1;
    // the other piece. it shares two vertices with the first one.
    rb.inset2[0] =  rb.inset1[0];
    rb.inset2[1] =  rb.inset1[1];
    rb.inset2[3] = -rb.inset1[3];

    v1 = rb.inset2[0] + rb.inset2[3];
    v2 = rb.inset2[3] - rb.inset2[0];
    t = cross_prod(XY, v2) / cross_prod(v1, v2);
    rb.inset2[2] = rb.inset2[3] + t * v1;
}

float getCross(vec2 p, Rhombus rb) {
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


void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
    vec2 uv = (fragCoord - iResolution.xy*.5)/iResolution.y;

    // zoom factor
    float zoom = iResolution.y > 600. ? 4.5 : 3.2;
    zoom *= 5. / float(N);
    uv *= zoom;

    float sf = 2. / clamp(iResolution.y, 300., 600.);

    init_grids();
    // p is transformed position of uv, vary its position by translating along
    // a fixed direction.
    vec2 p;
    Rhombus rb = get_mapped_rhombus(uv + iTime*0.2, p);
    get_tunnels(rb);

    // relative position of the transformed position with respect to rhombus center
    vec2 q = p - rb.cen;

    // assign a random number to each face, we let this random number vary by time
    // so the face can also vary its tunnel directions, openness, etc.
    float rnd = hash21(rb.cen);
    rnd = sin(rnd * 6.283 + iTime) * .5 + .5;

    float blink = smoothstep(0.15, .3, rnd);
    vec3 col = .5 + .45*cos(6.2831*rnd + vec3(0., 1., 2.) - .25);
    vec3 col2 = .5 + .45*cos(6.2831*dot(rb.cen, vec2(1.)) + vec3(2., 3., 1.) - .25);
    col = mix(col, pow(col*col2, vec3(.65))*2., .25);
    col = mix(col, col2.yxz,  float(rb.r * rb.s) / float(N*N*2)*blink);

    // cA and sA are the cos/sin of the angle at vertice A
    float cA = dot(grids[rb.r], grids[rb.s]);
    float sA = sqrt(1. - cA * cA);

    float dcen = dot(q, q) * .95;

    if(rnd > .2) {
        q.xy = -q.xy; // randomly flip the tunnels to make some cubes look impossible
        col *= max(1.25 - dcen, 0.);
    }
    else { col *= max(dcen + 0.55, 1.); }

    // distance to the boundary of the face
    float dface = sdPoly4(p, rb.verts);

    // distance to the face border
    float dborder = max(dface, -(dface + sf*4.));

    // distance to the tunnel of the face
    vec2 q1 = q * 4. / hs;
    float dtunnel = min(sdPoly4(q1, rb.inset1), sdPoly4(q1, rb.inset2));

    // distance to the hole of the face,
    // we choose the size of the hole to half the width/height of the rhombus.
    // note each rhombus has unit side length, so sA is twice the distance
    // from the center to its four edges.
    float dhole = dface + sA / hs;

    float dcross = 1e5;

#ifdef SOME_CLOSED_FACES
    // really dirty, maybe should put into a function
    if(abs(rnd - 0.5) > .495) {
        dhole += 1e5; dtunnel += 1e5;
        dcross = min(dcross, getCross(p, rb));
    }
#endif

    // shade the tunnels by the type of the rhombus
    float shade;

    float id = floor(hash21(vec2(float(rb.r), float(rb.s))) * float(N));

    // qd is our shading direction
    int ind = cA >= 0. ? 0 : 1;
    float qd = dot(q, rb.cen - rb.verts[ind]);

    shade = .7 -  smoothstep(-sf*2., sf*2., -sign(rnd - .5)*qd) * clamp(id/float(N), 0.2, 0.6);

    // draw the face border, multiply a factor 0.9 makes the edge look more antialiased
    col = mix(col, vec3(0), (1. - smoothstep(0., sf*2., dborder)) * 0.9);

    // add a thin bounding box around the hole
    col = mix(col, vec3(0), (1. - smoothstep(0., sf*4., abs(dface + sA/8.)))*.5);

    // draw the black hole
    col = mix(col, vec3(0), (1. - smoothstep(-sf*2., sf*2., dhole)));

    // shade the tunnels
    col = mix(col, vec3(1), (1. - smoothstep(-sf*4., 0., dtunnel-sf*4.)) * shade);

    // redraw the border of the hole to fix some tiny artifacts
    col = mix(col, vec3(0), (1. - smoothstep(0., sf*8., abs(dhole))));

    // highlight the edges
    col = mix(col, col * 1.5, (1. - smoothstep(sf*6., sf*12., dborder)) * .8);

    // draw the crosses on solid faces
    col = mix(col, vec3(0.), (1. - smoothstep(0., sf*6., dcross)) * .5);

    // adjust luminance of faces by their types
    col *= min(id / float(N) + .7, 1.);

    // draw hatch lines on the face to add some decorate pattern.
    // we get line direction first
    vec2 diag = (rb.verts[0] - rb.cen);
    float dd = cA < 0. ? dot(q, diag) : dot(q, vec2(-diag.y, diag.x));

    float hatch = clamp(sin(dd * 60. * PI) * 2. + .5, 0., 1.);
    float hrnd = hash21(floor(q * 40.) + 0.73);
    if (hrnd > 0.66) hatch = hrnd;

    // we dont't want the hatch lines to show on top of the hole and tunnel
    if (dtunnel < 0.0 || dhole < 0.0) hatch = 1.0;
    col *= hatch *.25 + .75;

    uv = fragCoord / iResolution.xy;
    col *= pow(16. * uv.x * uv.y * (1. - uv.x) * (1. - uv.y), .125) * .75 + .25;
    fragColor = vec4(sqrt(max(col, 0.0)), 1.0);
}
