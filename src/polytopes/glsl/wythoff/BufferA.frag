// responsible for handling mouse and setting global states

vec4 data = vec4(0); // data (fragment color) to write
ivec2 fc; // current fragment coords

// how quick to blend to target state
const float TARGET_LERP_RATE = 0.08;

// store a value in the current row (fc.y)
void store(int dst_col, vec4 dst_value) {
    if (fc.x == dst_col) { data = dst_value; }
}

//////////////////////////////////////////////////////////////////////
// do these settings represent a valid triangle?

bool valid_pqr(vec3 pqr) {
    float s = 1./pqr.x + 1./pqr.y + 1./pqr.z;
    return s > 1. && s < 1.3;
}

//////////////////////////////////////////////////////////////////////
// helper function for below

void update_snap(inout float dmin,
                 inout int imin,
                 in int i,
                 in vec3 q,
                 in vec3 p) {
    float d = length(p - q);
    if (d < dmin) {
        dmin = d;
        imin = i;
    }
}

//////////////////////////////////////////////////////////////////////
// given a position q on the sphere, see if it "snaps" to one of
// three triangle vertices or four "special points"

int tri_snap(in vec3 q) {
    float dmin = 1e5;
    int imin = -1;
    float ds = 1e5;

    for (int i=0; i<3; ++i) {
        update_snap(dmin, imin, i, q, tri_verts[i]);
        update_snap(dmin, imin, i+3, q, tri_spoints[i]);
        ds = min(ds, length(tri_spoints[i] - tri_spoints[3]));
    }

    update_snap(dmin, imin, 6, q, tri_spoints[3]);
    return dmin < max(0.5*ds, 0.125) ? imin: -1;
}

//////////////////////////////////////////////////////////////////////
// helper function for below

void update_closest(inout vec4 pd, in vec3 pi, in vec3 q) {
    float di = length(pi-q);
    if (di < pd.w) {
        pd.xyz = pi;
        pd.w = di;
    }
}

//////////////////////////////////////////////////////////////////////
// if q is in the triangle, return q; otherwise return closest point
// in triangle to q

vec3 tri_closest(vec3 q) {
    if (min(dot(q, tri_edges[0]),
            min(dot(q, tri_edges[1]), dot(q, tri_edges[2]))) > 0.) {
        return q;
    } else {
        vec4 pd = vec4(1e5);
        for (int i=0; i<3; ++i) {
            update_closest(pd, tri_verts[i], q);
            int j = (i+1)%3;
            int k = 3-i-j;
            vec3 Tji = tri_verts[j] - tri_verts[i];
            float u = clamp(dot(q - tri_verts[i], Tji) / dot(Tji, Tji), 0., 1.);
            vec3 p = normalize(tri_verts[i] + u*Tji);
            update_closest(pd, p, q);
        }
        return pd.xyz;
    }
}

//////////////////////////////////////////////////////////////////////
// handle clicking in bottom right inset depicting sphere

void gui_vertex_update() {
    if (fc.x != BARY_COL && fc.x != SPSEL_COL) { return; }
    if (length(iMouse.zw - inset_ctr)*inset_scl > 1.) {
        return;
    } else {
        vec3 q = sphere_from_gui(iMouse.xy);
        vec4 spsel;
        int s = tri_snap(q);
        if (abs(iMouse.zw) == iMouse.xy && s >= 0) {
            if (s < 3) {
                if (fc.x == BARY_COL) {
                    data.xyz = bary_from_sphere( tri_verts[s] );
                } else {
                    data = vec4(0);
                }
            } else {
                if (fc.x == BARY_COL) {
                    data.xyz = bary_from_sphere( tri_spoints[s-3] );
                } else {
                    data = vec4(0);
                    data[s-3] = 1.;
                }
            }
        } else {
            if (fc.x == BARY_COL) {
                data.xyz = bary_from_sphere( tri_closest(q) );
            } else {
                data = vec4(0);
            }
        }
    }
}

//////////////////////////////////////////////////////////////////////
// handle clicking triangle spin boxes

void gui_pqr_update() {
    if (fc.x != PQR_COL) { return; }
    for (int i=0; i<3; ++i) {
        int j = (i+1)%3;
        int k = 3-i-j;
        for (float delta=-1.; delta <= 1.; delta += 2.) {
            bool enabled = (delta < 0.) ? data[i] > 2. : data[i] < 5.;
            if (!enabled) { continue; }
            float d = box_dist(iMouse.xy, tri_ui_box(i, delta));
            if (d > 0.) { continue; }
            data[i] += delta;
            int iopp = delta*data[j] > delta*data[k] ? j : k;
            for (int cnt=0; cnt<5; ++cnt) {
                if (valid_pqr(data.xyz)) { continue; }
                data[iopp] -= delta;
            }
        }
    }
}

//////////////////////////////////////////////////////////////////////
// handle polyhedron rotation (time based or mouse based)

void gui_theta_update() {
    if (fc.x != THETA_COL) { return; }
    if (iMouse.z > 2.*inset_ctr.x && iMouse.w > 0.) {
        // mouse down somewhere in the pane but not in GUI panel
    	if ( length(iMouse.zw - object_ctr) < 0.45 * iResolution.y) {
            // down somewhere near object
            vec2 disp = (iMouse.xy - object_ctr) * 0.01;
            data.xyz = vec3(-disp.y, disp.x, 1);
        } else {
            // down far from object
            data.z = 0.;
        }
    }
    if (data.z == 0.) {
        float t = iTime;
        data.x = t * 2.*PI/6.;
        data.y = t * 2.*PI/18.;
    }
}

//////////////////////////////////////////////////////////////////////
// handle clicking on distance function selectors

void gui_dfunc_update() {
    if (!(fc.x == DFUNC0_COL || fc.x == DFUNC1_COL)) { return; }
    bool is_linked = (load(MISC_COL, TARGET_ROW).x != 0.);
    for (int row=0; row<2; ++row) {
        int col_for_row = (row == 0 ? DFUNC0_COL : DFUNC1_COL);
        for (int i=0; i<5; ++i) {
            bool update = ( (is_linked && fc.x == DFUNC1_COL) ||
                           (!is_linked && fc.x == col_for_row) );
            if (update) {
                if (box_dist(iMouse.xy, dfunc_ui_box(i, row)) < 0.) {
                    data = vec4(0);
                    if (i > 0) { data[i-1] = 1.; }
                }
            }
        }
    }
}

//////////////////////////////////////////////////////////////////////
// handle clicking on chain link icon or color selectors

void gui_misc_update() {
    if (fc.x != MISC_COL) { return; }
    if (box_dist(iMouse.xy, link_ui_box()) < 0.) {
        data.x = 1. - data.x;
    }
    for (int i=0; i<2; ++i) {
        if (box_dist(iMouse.xy, color_ui_box(i)) < 0.) {
            data.y = float(i);
        }
    }
}

//////////////////////////////////////////////////////////////////////
// handle clicking on decoration icons

void gui_decor_update() {
    if (fc.x != DECOR_COL) { return; }
    for (int i=0; i<4; ++i) {
        if (box_dist(iMouse.xy, decor_ui_box(i)) < 0.) {
            data[i] = 1. - data[i];
        }
    }
}

//////////////////////////////////////////////////////////////////////
// main "rendering" function

void main() {
    fc = ivec2(gl_FragCoord.xy);
    data = texelFetch(iChannel0, fc, 0);
    vec4 pqrx = load(PQR_COL, TARGET_ROW);
    float gui = 1.0;
    if (iFrame == 0) {
        // on first frame, store in default values
        store(PQR_COL, vec4(5, 3, 2, iTime));
        store(THETA_COL, vec4(0, 0, 0, 1));
        store(BARY_COL, vec4(0, 0, 0, 0));
        store(SPSEL_COL, vec4(0, 0, 0, 1));
        store(DFUNC1_COL, vec4(0, 1, 0, 0));
        store(DFUNC0_COL, vec4(0, 0, 0, 1));
        store(DECOR_COL, vec4(1));
        store(MISC_COL, vec4(0, 0, gui, 1));
    } else if (fc.y == TARGET_ROW) {
    	// target values are set by UI
        setup_gui(iResolution.xy, gui);
        setup_triangle(pqrx.xyz);
        float cur_mouse_state = min(iMouse.z, iMouse.w) > 0. ? 1. : -1.;
        bool click = (cur_mouse_state == 1. && pqrx.w <= 0.);
        if (fc.x == PQR_COL) {
            data.w = cur_mouse_state * iTime;
        }
        if (fc.x == MISC_COL) {
            data.z = gui;
        }
        float current_gui = load(MISC_COL, CURRENT_ROW).z;
        if (current_gui > 0.95) {
            if (click) {
                gui_pqr_update();
                gui_dfunc_update();
                gui_decor_update();
                gui_misc_update();
            }
            gui_vertex_update();
        }
        gui_theta_update();
    } else {
        vec4 cpqrx = load(PQR_COL, CURRENT_ROW);
        float dt = iTime - cpqrx.w;
        // current values are set by lerping towards target
        vec4 target = load(fc.x, TARGET_ROW);
        if (dt == 0.) {
            data = target;
        } else {
            data = mix(data, target, TARGET_LERP_RATE);
        }
        if (fc.x == PQR_COL) {
            data.w = abs(pqrx.w);
        }
    }
    fragColor = data;
}
