#version 130

uniform vec3 iResolution;
uniform float iTime;

out vec4 FinalColor;


#define PI 3.141592653
#define BIGF 100000.0


#define SOME_SOLID_FACES


// iq's hash function
float hash21(vec2 p)
{
    return fract(sin(dot(p, vec2(141.13, 289.97))) * 43758.5453);
}


// 2d cross product of two vectors.
// This is useful when we want to solve t for points p,q,v that p+t*q is parellel to
// v. Just use the fact ccross(p+tq, v) = 0 -> t = -ccross(p, v) / ccross(q, v)
float ccross(vec2 z, vec2 w)
{
    return z.x * w.y - z.y * w.x;
}


// distance from a 2d point p to a 2d segment (a, b) 
float dseg(vec2 p, vec2 a, vec2 b)
{
	vec2 v = b - a;
    p -= a;
    float t = clamp(dot(p, v)/ dot(v, v), 0., 1.);
    return length(p - t * v);
}


// check if a point p is in the convex cone t*a+s*b where t and s are both non-negative.
// again we use cross product to do this
bool incone(vec2 p, vec2 a, vec2 b)
{
    float cpa = ccross(p, a);
    if (cpa == 0.0) return true;
    float cpb = ccross(p, b);
    if (cpb == 0.0) return true;
    float cab = ccross(a, b);
    return (sign(cpb) == sign(cab)) && (sign(cpa) == sign(-cab)); 
}
    
    
// check if a 2d point p is inside a convex quad with vertices stored in a
// array of 2d vectors. Here we assume the vertices are aranged in order,
// either in clockwise order of anti-clockwise order.
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


// distance function from a 2d point p to a rhombus
// this is a signed distance version, points inside will return negative distances.
float dquad(vec2 p, vec2[4] verts)
{
    float dmin = dseg(p, verts[0], verts[1]);
    dmin = min(dmin, dseg(p, verts[1],  verts[2]));
    dmin = min(dmin, dseg(p, verts[2],  verts[3]));
    dmin = min(dmin, dseg(p, verts[3],  verts[0]));
    return inquad(p, verts) ? -dmin : dmin;
}


// shists of the grids
const float[5] shifts = float[5](0.5, 0.5, 0.5, 0.5, 0.5);

// directions of the grids, will be initialized in the beginning of the main function
vec2[5] grids;


// init the grid directions, we choose the fifth roots of unity
void init_grids()
{
    float theta;
    for(int k=0; k<5; k++)
    {
        theta = 2.0 * PI / 5.0 * float(k);
        grids[k] = vec2(cos(theta), sin(theta));
    }
}

// project a vector p to the k-th grid, note each grid line is shifted so we need
// to add the corresponding shifts.
float project_point_grid(vec2 p, int k)
{
    return dot(p, grids[k]) + shifts[k];
}

// for a point p and for each 0<=k<5, p must lie between the (m,m+1)-th lines in the k-th
// grid for some integer m.
// we use a bool param `lower` to choose either return m or m+1.
float[5] get_point_index(in vec2 p, bool lower)
{
    float[5] index;
    for(int k=0; k<5; k++)
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
    float[5] index = get_point_index(P, false);
    index[r] = kr; index[s] = ks;
    vec2 sum = vec2(0.0);
    for(int k=0; k<5; k++)
    {
        sum += grids[k] * index[k];
    }
    verts[0] = sum;
    verts[1] = sum + grids[r];
    verts[3] = sum + grids[s];
    verts[2] = verts[1] + grids[s];
}

// this is the "continous" transformation that maps a pixel to its position in the tiling
vec2 debruijn_transform(vec2 p)
{
    vec2 sum = vec2(0.0);
    for(int k=0; k<5; k++)
    {
        sum += grids[k] * project_point_grid(p, k);
    }
    return sum;
}

struct Rhombus
{
    // r, s for the r-th and s-th grids.
    int r;
    int s;
    // kr, ks for the lines in the two grids
    float kr;
    float ks;
    // center of the rhombus
    vec2 cen;
    vec2[4] verts;
    
    // the vertices of the tunnels. Each tunnel contains two pieces.
    vec2[4] inset1;
    vec2[4] inset2;
};

  
// a bit length computation to find after the transformation p --> q,
// which rhombus q lies in. we simply iterate over all possible combinations. 
Rhombus get_mapped_rhombus(vec2 p, out vec2 q)
{
    q = debruijn_transform(p);
    float[5] pindex = get_point_index(p, true);
    Rhombus rb;
    float kr, ks;
    vec2[4] verts;
    for(int r=0; r<4; r++)
    {
        for(int s=r+1; s<5; s++)
        {
            for(float dr=0.; dr<2.; dr+=1.0)
            {
                for(float ds=0.; ds<2.; ds+=1.0)
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

// for each tunnel in the face, we want it to slant by a best looking direction.
// We just choose a grid line direction which approx best with the diagonal line
// of this rhombus. This is used in Greg Egan's applet.
vec2 get_best_dir(int r, int s, vec2 v)
{
    float maxdot = 0.;
    float inn = 0.;
    vec2 result;
    for(int m=0; m<5; m++)
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


// compute the vertices of the two pieces of the tunnel
void get_tunnels(inout Rhombus rb)
{
    vec2 gr = grids[rb.r] / 2.;
    vec2 gs = grids[rb.s] / 2.;
    float cA = dot(gr, gs);
    float sgn = sign(cA);
    
    vec2 xy = (-gr + sgn * gs) / 2.;
    vec2 XY = get_best_dir(rb.r, rb.s, xy);
   
    XY /= 7.0;
    
    rb.inset1[0] = (gr - sgn * gs) / 2.;
    rb.inset1[1] = rb.inset1[0] + XY;
    rb.inset1[3] = (sgn * gr + gs) / 2.;
    vec2 v1 = rb.inset1[0] + rb.inset1[3];
    vec2 v2 = rb.inset1[3] - rb.inset1[0];
    float t = ccross(XY, v2) / ccross(v1,  v2);
    rb.inset1[2] =  rb.inset1[3] + t * v1;
    
    rb.inset2[0] =  rb.inset1[0];
    rb.inset2[1] =  rb.inset1[1];
    rb.inset2[3] = -rb.inset1[3];
	
    v1 = rb.inset2[0] + rb.inset2[3];
    v2 = rb.inset2[3] - rb.inset2[0];
    t = ccross(XY, v2) / ccross(v1,  v2);
    rb.inset2[2] =  rb.inset2[3] + t * v1;
    
}

void main()
{
    vec2 uv = gl_FragCoord.xy / iResolution.xy - 0.5;
    uv.y *= iResolution.y / iResolution.x;
    uv *= 6.0;
    
    init_grids();

    vec2 p;
    Rhombus rb = get_mapped_rhombus(uv + iTime * vec2(.5), p);
    get_tunnels(rb);

    // relative position of the transformed pixel in the rhombus
    vec2 q = p - rb.cen;
    
    float rnd = hash21(rb.cen);
    rnd = sin(rnd * 6.283 + iTime) * .5 + .5;
    
    
    // the blink and blend procedure are taken from shane's work
    vec3 col = vec3(1.0);
    float blink = smoothstep(0., .125, rnd - .15);

    float blend = dot(sin(uv*2.* PI - cos(uv.yx*PI*2.)*PI), vec2(.25)) + .5;
    col = max(col - mix(vec3(0, .6, .6), vec3(0, .3, .9), blend) * blink, 0.);
    col = mix(col, col.xzy, dot(sin(uv * 5. - cos(uv * 3. + iTime)), vec2(0.2)) + .7);
    col = mix(col, col.yxz, dot(sin(uv * 2. - cos(uv * 7. + iTime)), vec2(0.2)) + .35);
 
    float cA = dot(grids[rb.r], grids[rb.s]);
    float sA = sqrt(1. - cA * cA);
    float dcen = dot(q, q) * 1.5;
    
    if(rnd > .5)
    {
        q.xy = -q.xy; // randomly flip the tunnels to make some cubes look impossible
        col *= min(1.45 - dcen, .75);
    }
    else { col *= min(dcen + 0.75, .9); }
    
    // distance to the boundary of the face
    float dface = dquad(p, rb.verts);
    // distance to the tunnel of the face
    float tunnel = min(dquad(q, rb.inset1), dquad(q, rb.inset2));
	tunnel = max(tunnel, -(tunnel + 0.1));
    // distance to the hole of the face,
    // we choose the size of the hole to half the width/height of the rhombus.
    // note each rhombus has unit side length, so sA is twice the distance
    // from the center to its four edges.
    float hole = dface + sA / 4.0;
    float dcross = 1e5;

#ifdef SOME_SOLIDS_FACES
    
    if(abs(rnd - 0.5) > .48)
    {
        hole += 1e5; tunnel += 1e5; 
    	vec2 vA = (rb.verts[0] + rb.cen) / 2.;
        vec2 vB = (rb.verts[1] + rb.cen) / 2.;
    	vec2 vC = (rb.verts[2] + rb.cen) / 2.;
        vec2 vD = (rb.verts[3] + rb.cen) / 2.;
    	dcross = dseg(p, vA, vB);
        dcross = min(dcross, dseg(p, vB, vC));
        dcross = min(dcross, dseg(p, vC, vD));
        dcross = min(dcross, dseg(p, vD, vA));
        dcross = min(dcross, dseg(p, vA, vC));
        dcross = min(dcross, dseg(p, vB, vD));
    }
#endif
    
    // combine all distances
    float dborder = max(dface, -(dface + 0.006));
    dborder = min(dborder, min(tunnel, hole));
    
    // shade the tunnels by the type of the rhombus
    float shade;
    float id = floor(hash21(vec2(float(rb.r), float(rb.s))) * 3.);
    // qd is our shading direction
    float qd = dot(q, rb.cen - rb.verts[2]);
    if(id == 0.)
        shade = .8 -  step(0., -sign(rnd - .5)*qd) * .3;
    else if(id == 1.)
        shade = .6 -  step(0., -sign(rnd - .5)*qd) * .4;
    else
        shade = .7 -  step(0., -sign(rnd - .5)*qd) * .2;
    
    col = mix(col, vec3(0.), (1. - smoothstep(0., .01, hole)) * .8);
    col = mix(col, vec3(0.), (1. - smoothstep(0., .01, dborder)) * .95);
    // shade the tunnels
    col = mix(col, vec3(1.), (1. - smoothstep(0., .01, tunnel)) *shade);
    // highlighting the edges
    col = mix(col, col * 2., (1. - smoothstep(0., .02, dborder - .02))*.3);
    // highlight crosses on solid faces
    col = mix(col, vec3(0.), (1. - smoothstep(0., .01, dcross-0.005)) * 0.5);
    col *= min(id / 2. + .5, 1.25);

    vec2 diag = (rb.verts[0] - rb.cen);
    float dd = cA < 0. ? dot(q, diag) : dot(q, vec2(-diag.y, diag.x));
    // some hatch lines to make the faces look like pencil work
    float hatch = clamp(sin(dd * 60.*PI) * 2. + .5, 0., 1.);
    float hrnd = hash21(floor(q * 400.* PI) + 0.73);
    if (hrnd > 0.66) hatch = hrnd;
    // we dont't want the hatch lines to show on top of the hole and tunnel
    if (tunnel < 0.0 || hole < 0.0) hatch = 1.0;
    col *= hatch *.1 + .85;
    // some thin bouding box between the hole and the face border
    col = mix(col, vec3(0.), (1. - smoothstep(0., .01, max(dface+0.1, -(dface+.1))))*.5);

    uv =  gl_FragCoord.xy / iResolution.xy;
    col *= pow(16. * uv.x * uv.y * (1. - uv.x) * (1. - uv.y), .125) * .75 + .25;
    FinalColor = vec4(sqrt(max(col, 0.0)), 1.0);
}
