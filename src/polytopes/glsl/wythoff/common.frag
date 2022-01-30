#version 130

uniform vec3          iResolution;
uniform float         iTime;
uniform vec4          iMouse;
uniform int           iFrame;
uniform sampler2D     iTexture;
uniform sampler2D     iChannel0;
uniform sampler2D     iChannel1;
uniform int           AA;

out vec4 fragColor;


// mostly code for triangle setup and coordinate projection
// also gui placement

const float PI = 3.141592653589793;
const float TOL = 1e-5;

// define this to see some interesting visualization
// (and to speed up compile!)
//#define STEREOGRAPHIC_POLAR

//////////////////////////////////////////////////////////////////////
// state storage

#define PQR_COL     0
#define THETA_COL   1
#define BARY_COL    2
#define SPSEL_COL   3
#define DFUNC0_COL  4
#define DFUNC1_COL  5
#define DECOR_COL   6
#define MISC_COL    7

// link, shade per face, GUI, debugbgcolor

#define TARGET_ROW  0
#define CURRENT_ROW 1

#define load(x,y)  texelFetch(iChannel0, ivec2(x,y), 0)
#define load4(a,b) load(a,b)
#define load3(a,b) load(a,b).xyz
#define load2(a,b) load(a,b).xy
#define load1(a,b) load(a,b).x

//////////////////////////////////////////////////////////////////////
// triangle layout (see setup_triangle below)

vec3 pqr;

mat3 tri_edges, tri_verts, poly_edges, ortho_proj, planar_proj;
mat4x3 tri_spoints;
bvec3 is_face_normal;

mat3x2 planar_verts;
mat2 bary_mat;

vec3 bary_poly_vertex;
vec4 spoint_selector = vec4(0.0);
vec3 poly_vertex;

//////////////////////////////////////////////////////////////////////
// GUI layout (see setup_gui below)

float inset_scl;
vec2 inset_ctr;
vec2 object_ctr;
float text_size;
float dfunc_y;


mat2 inverse(mat2 m) {
    float det = m[0][0] * m[1][1] - m[0][1] * m[1][0];
    return mat2(m[1][1], -m[0][1], -m[1][0], m[0][0]) / det;
}

//////////////////////////////////////////////////////////////////////
// stereographic projection

vec2 planar_from_sphere(vec3 q) {
    q = q * planar_proj;
    return q.xy / q.z;
}

vec3 sphere_from_planar(vec2 p) {
    return planar_proj * vec3(p, 1.0);
}

//////////////////////////////////////////////////////////////////////
// cartesian <-> barycentric

vec3 bary_from_planar(vec2 p) {
    vec2 bxy = bary_mat * (p - planar_verts[2]);
    return vec3(bxy, 1.0 - bxy.x - bxy.y);
}

vec2 planar_from_bary(vec3 b) {
    return planar_verts * b;
}

//////////////////////////////////////////////////////////////////////
// 3D <-> barycentric (via sterographic projection)

vec3 bary_from_sphere(vec3 q) {
    return bary_from_planar(planar_from_sphere(q));
}

vec3 sphere_from_bary(vec3 b) {
    return tri_verts * b;
}

//////////////////////////////////////////////////////////////////////
// given polyhedron vertex coords as barycentric coords,
// compute where it should be on sphere (but first check)
// if it should be at a "special" point

void poly_from_bary() {
    bool was_select = false;

    for (int i=0; i<4; ++i) {
        if (abs(spoint_selector[i] - 1.0) < TOL) {
            poly_vertex = tri_spoints[i];
            bary_poly_vertex = bary_from_sphere(poly_vertex);
            was_select = true;
        }
    }
    if (!was_select) {
        poly_vertex = normalize(sphere_from_bary(bary_poly_vertex.xyz));
    }
}

//////////////////////////////////////////////////////////////////////
// map 2D position in lower right inset of gui to 3D sphere pos

vec3 sphere_from_gui(in vec2 p) {
    p -= inset_ctr;
    p *= inset_scl;
    float dpp = dot(p, p);

    if (dpp >= 1.0) {
        return vec3(p/sqrt(dpp), 0.0);
    }
    else {
        vec3 p3d = vec3(p, sqrt(1.0 - dot(p, p)));
        return ortho_proj * p3d;
    }
}

//////////////////////////////////////////////////////////////////////
// given PQR and specification of polygon vertex, set up all of the
// static info we need to do Wythoff construction later

void setup_triangle(in vec3 new_pqr) {
    pqr = new_pqr;
    float p = pqr.x;
    float q = pqr.y;
    float r = pqr.z;
    float tp = PI / p;
    float tq = PI / q;
    float tr = PI / r;

    float cp = cos(tp), sp = sin(tp);
    float cq = cos(tq);
    float cr = cos(tr);

    vec3 lr = vec3(1, 0, 0);
    vec3 lq = vec3(-cp, sp, 0);
    vec3 lp = vec3(-cq, -(cr+cp*cq)/sp, 0);

    lp.z = sqrt(1.0 - dot(lp.xy, lp.xy));

    tri_edges = mat3(lp, lq, lr);

    vec3 P = normalize(cross(lr, lq));
    vec3 R = normalize(cross(lq, lp));
    vec3 Q = normalize(cross(lp, lr));

    tri_verts = mat3(P, Q, R);

    tri_spoints[0] = normalize(R + Q);
    tri_spoints[1] = normalize(P + R);
    tri_spoints[2] = normalize(P + Q);

    tri_spoints[3] = normalize(P + Q + R);

    ortho_proj[2] = tri_spoints[3];
    ortho_proj[0] = -normalize(cross(ortho_proj[2], tri_edges[1]));
    ortho_proj[1] = normalize(cross(ortho_proj[2], ortho_proj[0]));

    planar_proj[2] = normalize(cross(R-P, Q-P));

    planar_proj[0] = -normalize(cross(planar_proj[2], tri_edges[1]));
    planar_proj[1] = normalize(cross(planar_proj[2], planar_proj[0]));

    for (int i=0; i<3; ++i) {
        planar_verts[i] = planar_from_sphere(tri_verts[i]);
    }

    bary_mat = inverse(mat2(planar_verts[0] - planar_verts[2],
                            planar_verts[1] - planar_verts[2]));

    poly_from_bary();

    is_face_normal = bvec3(true);

    for (int i=0; i<3; ++i) {
        poly_edges[i] = normalize(cross(poly_vertex, tri_edges[i]));
        for (int j=0; j<2; ++j) {
            int vidx = (i+j+1)%3;
            if (abs(dot(tri_verts[vidx], poly_edges[i])) < TOL) {
                is_face_normal[vidx] = false;
            }
        }
    }
}

//////////////////////////////////////////////////////////////////////
// if point p lies opposite m, mirror it. return the transform that
// accomplishes this.

mat3 mirror(inout vec3 p, in vec3 m) {
    float d = dot(p, m);
    mat3 rval = mat3(1.0) - (2.0 * step(d, 0.)) * outerProduct(m, m);
    p = rval * p;
    return rval;
}

//////////////////////////////////////////////////////////////////////
// modify the vector m to halve the angle with respect to the y
// axis (assume that m.z == 0)

vec3 half_angle(in vec3 m) {
    return normalize(vec3(m.x - 1.0, m.y, 0.0));
}

//////////////////////////////////////////////////////////////////////
// use space folding to make sure pos lies in the triangular cone
// whose edge planes are given by tri_edges
//
// this function was largely determined by trial and error. possibly
// if I understood more about symmetry I would be able to get it
// a little simpler

mat3 tile_sphere(inout vec3 pos) {
    mat3 M = mat3(1.0);

    ////////////////////////////////////////////////////
    // part 1: guarantee that the point lives inside
    // the cluster of p triangles that share the vertex
    // (0, 0, 1)

    M *= mirror(pos, vec3(1, 0, 0));

    vec3 m = tri_edges[0];

    for (float i=0.0; i<5.0; ++i) {
        // mirror
        M *= mirror(pos, m);
        m -= tri_edges[1] * 2.0 * dot(m, tri_edges[1]);
        M *= mirror(pos, m);
        m -= tri_edges[2] * 2.0 * dot(m, tri_edges[2]);
    }

    ////////////////////////////////////////////////////
    // part 2: fold in the XY plane to make sure the
    // point lives in the triangular cone just to the
    // right of the y axis

    M *= mirror(pos, vec3(1, 0, 0));
    float p = pqr.x;
    float k = p >= 5.0 ? 4. : p >= 3.0 ? 2. : 1.;
    float theta = k * PI / p;
    m = vec3(-cos(theta), sin(theta), 0); // lq

    if (p >= 5.0) {
        M *= mirror(pos, m);
        m = half_angle(m);
    }

    if (p >= 3.0) {
        M *= mirror(pos, m);
        m = half_angle(m);
    }

    M *= mirror(pos, m);
    return M;
}

//////////////////////////////////////////////////////////////////////
// rotate about x-axis

mat3 rotX(in float t) {
    float cx = cos(t), sx = sin(t);
    return mat3(1., 0, 0,
                0, cx, sx,
                0, -sx, cx);
}

//////////////////////////////////////////////////////////////////////
// rotate about y-axis

mat3 rotY(in float t) {
    float cy = cos(t), sy = sin(t);
    return mat3(cy, 0, -sy,
                0, 1., 0,
                sy, 0, cy);
}

//////////////////////////////////////////////////////////////////////
// GUI box placement functions

float box_dist(vec2 p, vec4 b) {
    p = abs(p - b.xy) - b.zw;
    return max(p.x, p.y);
}

vec4 char_ui_box(int idx) {
    const vec2 digit_rad = vec2(0.35, 0.5);
    return vec4(inset_ctr.x + (float(idx - 1)) * text_size,
                2.0*inset_ctr.y + 1.15*text_size,
                digit_rad * text_size);
}

vec4 tri_ui_box(int idx, float delta) {
    return vec4(char_ui_box(idx).xy + vec2(0, 0.9*delta*text_size),
                0.4*text_size, 0.3*text_size);
}

vec4 dfunc_ui_box(int idx, int row) {
    return vec4(inset_ctr.x + (float(idx - 2))*text_size,
    	        dfunc_y - float(1-row)*text_size,
                vec2(0.45*text_size));
}

vec4 link_ui_box() {
    return vec4(inset_ctr.x + 2.85*text_size,
                dfunc_y - 0.5*text_size,
                0.3*text_size, 0.5*text_size);
}

vec4 decor_ui_box(int idx) {
    return vec4(inset_ctr.x + (float(idx)-1.5)*text_size*1.1,
                dfunc_y - 2.5*text_size,
                vec2(0.45*text_size));
}

vec4 color_ui_box(int idx) {
    return vec4(inset_ctr.x + (float(idx)-0.5)*text_size,
                dfunc_y - 3.5*text_size,
                vec2(0.45*text_size));
}

//////////////////////////////////////////////////////////////////////
// set up GUI positions

void setup_gui(vec2 res, float gui) {
    //bool show_gui = gui > 0.99 && res.y > 250.;
    if (res.y < 250.) { gui = 0.0; }
    float inset_sz = 0.20*res.y;
    float margin_px = 6.0;
    text_size = 0.06 * res.y;
    inset_scl = 1.0 / inset_sz;
    inset_sz += margin_px;
    inset_ctr = vec2(mix(-inset_sz, inset_sz, gui), inset_sz);
    object_ctr = vec2(0.5*res.x + gui*inset_sz, 0.5*res.y);
    dfunc_y = res.y - text_size;
}
