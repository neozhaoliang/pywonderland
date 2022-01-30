// distance marches and shades the polyhedron

const int rayiter = 8;
vec3 L = normalize(vec3(-0.7, 1.0, -1.0));

const float dmin = 2.0;
const float dmax = 5.0;

vec4 distance_function;
float shade_per_face;
float bg_value;
vec4 decorations;

//////////////////////////////////////////////////////////////////////
// data structure for polyhedron distance queries

struct query_t {

    int vidx; // index of triangle vertex
    int eidx; // index of triangle edge

    float fdist_vertex; // 3D distance to closest vertex
    float fdist_edge;   // 3D distance to closest edge/vertex
    float fdist_face;   // 3D distance to closest face/edge/vertex

    float pdist_tri;       // distance to triangle cutting plane
    float pdist_poly_edge; // SIGNED distance to polyhedron edge cutting plane (pass thru ctr)
    float pdist_poly_perp; // perpendicular distance to polyhedron edge (parallel to face)
    float pdist_bisector;  // distance to polyhedron edge bisector cutting plane

    mat3 M; // 3D flip to move point inside spherical triangle
};

//////////////////////////////////////////////////////////////////////
// wythoff construction - the workhorse of the distance estimator.

void construct(in vec3 pos, out query_t Q) {
    // flip point to land within spherical triangle
    Q.M = tile_sphere(pos);

    // position relative to vertex
    vec3 rel_pos = pos - poly_vertex;

    // initialize data structure members that get updated
    // as the loop progresses
    Q.fdist_vertex = length(rel_pos);
    Q.fdist_edge = Q.fdist_vertex;
    Q.pdist_tri = 1e5;

    // for each potential face edge (perpendicular to each tri. edge)
    for (int eidx=0; eidx<3; ++eidx) {
        vec3 tri_edge = tri_edges[eidx];

        // update distance to triangle
        Q.pdist_tri = min(Q.pdist_tri, dot(pos, tri_edge));

        // signed distance of polyhedron vertex poly_vertex from edge plane
        float V_tri_dist = dot(poly_vertex, tri_edge);

        // polyhedron edge cut plane (passes thru origin and V, perpendicular
        // to triangle edge)
        vec3 poly_edge = poly_edges[eidx];

        // signed distance from point to face edge
        float poly_edge_dist = dot(pos, poly_edge);

        // triangle vertex on the same side of face edge as point
        int vidx = (eidx + (poly_edge_dist > 0. ? 2 : 1)) % 3;

        // see which side of the vertex we are on
        float rel_tri_dist = dot(rel_pos, tri_edge);

		// update distance to edge
        Q.fdist_edge = min(Q.fdist_edge, length(rel_pos - min(rel_tri_dist, 0.) * tri_edge));

        // construct at the other polyhedron edge associated with the given
        // triangle vertex
        vec3 other_poly_edge = poly_edges[3-eidx-vidx];

        // construct the plane that bisects the two polyhedron edges
        vec3 bisector = cross(poly_vertex, poly_edge - other_poly_edge);

        float bisector_dist = dot(pos, bisector);

        if (bisector_dist > 0.) {
            // if we are on the correct side of the associated
            // bisector, than we have found the closest triangle
            // edge & vertex.

            Q.pdist_bisector = bisector_dist;
            Q.pdist_poly_edge = poly_edge_dist;
            Q.eidx = eidx;
            Q.vidx = vidx;
        }
    }

    // computing the perpendicular distance away from
    // the polyhedron edges was a bit hairy. there
    // was probably a better way to do this.

    // initialize to zero
    Q.pdist_poly_perp = 1e5;

    // for each triangle vertex
    for (int vidx=0; vidx<3; ++vidx) {

        if (!is_face_normal[vidx]) { continue; }

        vec3 tri_vertex = tri_verts[vidx];

        // midpoint of polyhedron face
        vec3 P = tri_vertex * dot(poly_vertex, tri_vertex);

        // initial big negative perpendicular distance
        float pp = -1e5;

        // for each triangle edge associated with the vertex
        for (int j=0; j<2; ++j) {

            int eidx = (vidx+j+1)%3;

            // constructed same as big for loop above
            vec3 tri_edge = tri_edges[eidx];

            // midpoint of polyhedron edge
            vec3 F = poly_vertex - dot(poly_vertex, tri_edge)*tri_edge;

            // mix in signed distance perpendicular to edge
            pp = max(pp, dot(rel_pos, normalize(F - P)));

        }
        Q.pdist_poly_perp = min(Q.pdist_poly_perp, pp);
    }
    if (Q.pdist_poly_perp < 0.) {
        // only use true distance to face if we are "above" it
        Q.fdist_face = dot(rel_pos, tri_verts[Q.vidx]);
    } else {
        // otherwise just use distance to edge
        Q.fdist_face = Q.fdist_edge;
    }
}

//////////////////////////////////////////////////////////////////////
// distance estimator weighs a linear combination of different
// distance functions

vec2 map(in vec3 pos) {
    query_t Q;
    construct(pos, Q);
    mat4x2 tm;
    // distance to sphere
    vec2 sphere = vec2(length(pos)-1., 2);

    // distance to polyhedron
	tm[0] = vec2(Q.fdist_face, 2);

    // distance to ball-and-stick web (cylinders/spheres)
    vec2 dv = vec2(Q.fdist_vertex-0.07, 0);
    vec2 de = vec2(Q.fdist_edge-0.04, 1);
    tm[1] = dv.x < de.x ? dv : de;

    // distance to polyhedral net (faceted edges)
    tm[2] = vec2(max(-(Q.pdist_poly_perp+0.08),
                     max(Q.fdist_face, -0.08-Q.fdist_face)), 1);

    // distance to polyhedron dilated by sphere
    tm[3] = vec2(Q.fdist_face-0.15, 2);

    // sphere coefficient
    float k = 1.0 - dot(distance_function, vec4(1));

    // return final linear combination
    return (k*sphere + tm * distance_function);
}

//////////////////////////////////////////////////////////////////////
// IQ's normal calculation.

vec3 calcNormal( in vec3 pos ) {
    vec3 eps = vec3( 0.01, 0.0, 0.0 );
    vec3 nor = vec3(
        map(pos+eps.xyy).x - map(pos-eps.xyy).x,
        map(pos+eps.yxy).x - map(pos-eps.yxy).x,
        map(pos+eps.yyx).x - map(pos-eps.yyx).x );
    return normalize(nor);
}

//////////////////////////////////////////////////////////////////////
// IQ's distance marcher.

vec2 castRay( in vec3 ro, in vec3 rd ) {
    const float precis = 0.001;
    float h=dmin;
    float t = 0.0;
    float m = -1.0;

    for(int i=0; i<40; i++ ) {
        if(abs(h) < precis || t > dmax)
            break;
        t += h;
        vec2 res = map( ro+rd*t );
        h = res.x;
        m = res.y;
    }
    if (t > dmax) {
        m = -1.0;
    }
    return vec2(t, m);
}

//////////////////////////////////////////////////////////////////////
// coloring function for surface shading - input is position and
// material (0=vertex, 1=edge, 2=face)

vec3 poly_color(vec3 pos, float material) {
    // do our distance query with the given point
    query_t Q;
    construct(pos, Q);

    // this would be an odd failure but it happened
    // sometimes during debugging
    if (Q.vidx < 0) {return vec3(0.9); }

    // "standard" blue/yellow/red vertex colors
    const mat3 std_fcolors = mat3(vec3(0, 0, 1),
                               vec3(1, 1, 0),
                               vec3(1, 0, 0));

    // for coloring with faces - gives a nice contrast to
    // the bgcolors above
    const mat3 std_ecolors = mat3(vec3(1, 0.5, 0),
                              vec3(0.5, 0, 1),
                              vec3(0, 0.5, 0));

    const vec3 std_vert = vec3(0.1, 0.2, 0.5);

    ////////////////////////////////////////////////////////////
    // start setting up some AA for face coloring
    //
    // Q.vidx is the index of the triangle vertex that forms
    // the normal of this face
    //
    // Q.eidx is the index of the triangle edge perpendicular
    // to the polyhedron edge
    //
    // now we want to find the index of the triangle vertex
    // which lies *across* this polyhedron edge (this is for
    // anti-aliasing using the "standard" color scheme

    // start with other vertex on this triangle edge,
    // and see if it is also on this polyhedron edge
    int vidx2 = 3 - Q.vidx - Q.eidx;

    vec3 opposite_tri_vertex = tri_verts[vidx2];
    float opp_on_edge = abs(dot(opposite_tri_vertex, poly_edges[Q.eidx]));

    // if so, then the same triangle vertex is used as normal
    // for both faces (just in an adjacent triangle)
    if (opp_on_edge < TOL) { vidx2 = Q.vidx; }

    vec3 tri_vert2 = tri_verts[vidx2];

    if (vidx2 == Q.vidx) {
         tri_vert2 = reflect(tri_vert2, poly_edges[Q.eidx]);
    }

    // hacked scaling factor for antialiasing -- should probably
    // be based on ray differentials, but in practice this works fine
    float s = 2.5/iResolution.y;

    // blend coefficient for blending between two different face colors
    float u_face_aa = smoothstep(-0.5*s, 0.5*s, abs(Q.pdist_poly_edge));

    // get antialiased standard face color and face normal
    vec3 std_face_aa = mix(std_fcolors[vidx2], std_fcolors[Q.vidx], u_face_aa);
    vec3 sph_face_aa = mix(tri_vert2, tri_verts[Q.vidx], u_face_aa);

    ////////////////////////////////////////////////////////////
    // AA for edge coloring

    // get blended edge color (probably a smarter way to antialias)
    vec3 std_edge_aa = mix(std_ecolors*vec3(0.33333), std_ecolors[Q.eidx],
                           smoothstep(0., s, Q.pdist_bisector));

    // midpoint of closest polygon edge
    vec3 edge_midpoint = poly_vertex - dot(tri_edges[Q.eidx], poly_vertex)*tri_edges[Q.eidx];

    // plane splitting face thru polyhedron vertex and face center
    vec3 face_split = normalize(cross(tri_verts[Q.vidx], poly_vertex));

    // same midpoint across splitline
    vec3 opp_edge_midpoint = reflect(edge_midpoint, face_split);

    // edges should blend together at polyhedron vertex
    vec3 sph_edge_aa = mix(poly_vertex, edge_midpoint,
                         smoothstep(0., s, Q.pdist_bisector));

    // edges should blend together near corners of face
    sph_edge_aa = mix(opp_edge_midpoint, sph_edge_aa,
                      smoothstep(-0.5*s, 0.5*s, abs(dot(pos, Q.M*face_split))));

    ////////////////////////////////////////////////////////////
    // now put it all together

    // blend between standard and spherical shading
    vec3 face = mix(std_face_aa, 0.5*(Q.M*sph_face_aa)+0.5, shade_per_face);
    vec3 edge = mix(std_edge_aa, 0.5*(Q.M*sph_edge_aa)+0.5, shade_per_face);
    vec3 vert = mix(std_vert, 0.25*(Q.M*poly_vertex)+0.75, shade_per_face);

    // blend face, verts, edges with decorations
    vec3 color = face;

    // vertex and polyhedron edge decorations affect just face
    float scaled_vertex_distance = length(pos - Q.M*poly_vertex*length(pos));
    color *= mix(1.0, 0.0,
                max(decorations.x*smoothstep(s, 0.0, scaled_vertex_distance-0.02),
                    decorations.y*smoothstep(s, 0.0, abs(Q.pdist_poly_edge)-.5*s)));

    // edge colors
    color = mix(color, edge, clamp(2. - material, 0.0, 1.0));

    // parity & triangle edges affect face & edge
    float parity = dot(Q.M[0], cross(Q.M[1], Q.M[2]));

    color *= mix(1.0, 0.8, decorations.w*smoothstep(0.5*s, -0.5*s, parity*Q.pdist_tri));
    color *= mix(1.0, 0.5, decorations.z*smoothstep(s, 0.0, abs(Q.pdist_tri)));

    // vertex colors
    color = mix(color, vert, clamp(1. - material, 0.0, 1.0));

    //done
    return color;
}

//////////////////////////////////////////////////////////////////////
// trace ray & determine fragment color

vec4 shade( in vec3 ro, in vec3 rd ){
    vec2 tm = castRay(ro, rd);
    vec3 c;
    if (tm.y < 0.0) {
        tm.x = dmax;
        c = vec3(bg_value);
    } else {
        vec3 pos = ro + tm.x*rd;
        vec3 n = calcNormal(pos);
        vec3 color = poly_color(pos, tm.y);
        vec3 diffamb = (0.9*clamp(dot(n,L), 0.0, 1.0)+0.1) * color;
        vec3 p = normalize(pos);
        vec3 refl = 2.0*n*dot(n,L)-L;
        float spec = 0.4*pow(clamp(-dot(refl, rd), 0.0, 1.0), 20.0);
        c = diffamb + spec;
        c *= 0.4*dot(p, n) + 0.6;
    }
    return vec4(c, tm.x);
}

//////////////////////////////////////////////////////////////////////
// generate polyhedron image finally

void main() {

#ifdef STEREOGRAPHIC_POLAR

    fragColor = vec4(1, 1, 1, dmax);

#else

    ////////////////////////////////////////////////////////////
    // load in settings from GUI manager

    // load triangle shape & rotation from target row (set directly)
    vec4 pqrx = load4(PQR_COL, TARGET_ROW);
    vec4 theta = load4(THETA_COL, TARGET_ROW);
    vec4 cpqrx = load4(PQR_COL, CURRENT_ROW);
    float dt = iTime - cpqrx.w;
    int active_row = CURRENT_ROW;
    if (dt == 0.) {
        active_row = TARGET_ROW;
    }
    // all other params change continuously
    bary_poly_vertex = load3(BARY_COL, active_row);
    spoint_selector = load4(SPSEL_COL, active_row);
    vec4 misc = load4(MISC_COL, active_row);
    vec4 df1 = load4(DFUNC1_COL, active_row);
    vec4 df0 = mix(load4(DFUNC0_COL, active_row), df1, misc.x);
    decorations = load4(DECOR_COL, active_row);
    shade_per_face = misc.y;
    bg_value = misc.w;
    distance_function = mix(df0, df1, smoothstep(0.25, 0.75, gl_FragCoord.y / iResolution.y));
    setup_triangle(pqrx.xyz);
    setup_gui(iResolution.xy, misc.z);

    ////////////////////////////////////////////////////////////
    // pretty normal raymarcher/renderer from here on out
    // only twist is that emit ray distance along with
    // color to final buffer in order to do AA along
    // depth discontinuities

    const vec3 tgt = vec3(0.0, 0.0, 0.0);
    const vec3 cpos = vec3(0.0, 0.0, 3.25);
    const vec3 up = vec3(0, 1, 0);
    vec3 rz = normalize(tgt - cpos),
        rx = normalize(cross(rz,vec3(0,1.,0))),
        ry = cross(rx,rz);
    mat3 Rview = mat3(rx,ry,rz)*rotY(theta.y)*rotX(theta.x);
    L = Rview*L;
    vec4 tot = vec4(0.0);
    for (int ii = 0; ii < AA; ii ++) {
        for (int jj = 0; jj < AA; jj++) {
            vec2 offset = vec2(float(ii), float(jj)) / float(AA);
            vec2 uv = (gl_FragCoord.xy + offset - object_ctr) * 0.8 / (iResolution.y);
            vec3 rd = Rview*normalize(vec3(uv, 1.));
            vec3 ro = tgt + Rview*vec3(0,0,-length(cpos-tgt));
            tot += shade(ro, rd);
        }
    }
    fragColor = tot / float(AA * AA);
#endif
}
