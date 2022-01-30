//#define DEBUG_HITBOXES
#define ENABLE_EDGE_AA

//////////////////////////////////////////////////////////////////////
// point-line distance

float dline(vec2 p, vec2 a, vec2 b) {
    vec2 ba = b-a;
    vec2 n = normalize(vec2(-ba.y, ba.x));
    return dot(p-a, n);
}

//////////////////////////////////////////////////////////////////////
// point-line and point-segment distance

vec2 dline_seg(vec2 p, vec2 a, vec2 b) {
    vec2 ba = b-a;
    vec2 n = normalize(vec2(-ba.y, ba.x));
    vec2 pa = p-a;
    float u = clamp(dot(pa, ba)/dot(ba, ba), 0., 1.);
    return vec2(dot(a-p, n), length(p-mix(a,b,u)));
}

//////////////////////////////////////////////////////////////////////
// distance to character in SDF font texture

float font2d_dist(vec2 tpos, float size, vec2 offset) {
    float scl = 0.63/size;
    vec2 uv = tpos*scl;
    vec2 font_uv = (uv+offset+0.5)*(1.0/16.0);
    float k = texture(iTexture, font_uv, -100.0).w + 1e-6;
    vec2 box = abs(uv)-0.5;
    return max(k-127.0/255.0, max(box.x, box.y))/scl;
}

//////////////////////////////////////////////////////////////////////
// distance to triangle for spin box

float spin_icon_dist(vec2 pos, float size, bool flip, bool dim) {
    if (flip) { pos.y = -pos.y; }
    pos.x = abs(pos.x);
    vec2 p0 = vec2(0, -0.7)*text_size;
    vec2 p1 = vec2(0.35, -0.7)*text_size;
    vec2 p2 = vec2(0.0, -1.1)*text_size;
    float d = max(dline(pos, p0, p1), dline(pos, p1, p2));
    if (dim) {
        d = abs(d + 0.02*text_size) - 0.02*text_size;
    }
    return d;
}

//////////////////////////////////////////////////////////////////////
// distance to icon for distance function

float dfunc_icon_dist(vec2 p, float sz, int style) {
    if (style == 0) {
        return length(p) - sz;
    } else if (style == 5 || style == 6) {
		p.y = abs(p.y);
        vec2 vp = p*vec2(1, 0.9);
        float d = abs(length((vp - vec2(0, 0.6*sz))) - 0.5*sz) - 0.06*sz;
        float q = length(p - vec2(0, min(p.y, 0.4*sz)))-0.06*sz;
        float r = box_dist(p, vec4(0, 0, 0.35, 0.7)*sz);
        if (style == 6) {
            q = min(q, box_dist(p, vec4(0, 2.0, 0.06, 0.46)*sz));
            q = min(q, box_dist(p, vec4(-0.5, 2.4, 0.56, 0.06)*sz));
        }
        return min(q, max(d, -r));
    }
    p += vec2(0, 0.15*sz);
    sz *= 0.9;
    const float k = 0.8660254037844387;
    p.x = abs(p.x);
    vec2 m0 = vec2(0, sz);
    vec2 m1 = vec2(k*sz, -0.5*sz);
    vec2 m2 = vec2(0, -0.5*sz);
    vec2 d_ls = min(dline_seg(p, m0, m1),
                    dline_seg(p, m1, m2));
    float d_point = min(length(p - m0), length(p - m1));
    if (style == 1) {
        return -d_ls.x - 0.5;
    } else if (style == 2) {
        return min(d_point - 0.25*sz, abs(d_ls.y)-0.08*sz);
    } else if (style == 3) {
        return abs(d_ls.x)-0.15*sz;
    } else {
        return min(min(d_ls.y, d_point) - 0.35*sz, -d_ls.x);
    }
}

//////////////////////////////////////////////////////////////////////
// distance to icon for decorations

float decor_icon_dist(vec2 p, float sz, int style) {
    float s = sign(p.x*p.y);
    p = abs(p);
    vec2 a = vec2(0, sz);
    vec2 b = vec2(sz, 0);
    float l = dline(p, a, b);
    float c = length( p - (p.x > p.y ? b : a)*0.8 );
    if (style == 0) {
        return c - 0.2*sz;
    } else if (style == 1) {
        return abs(l + 0.04*sz) - 0.08*sz;
    } else if (style == 2) {
        return min(abs(l), max(min(p.x, p.y), l)) - 0.03*sz;
    } else {
        return min(max(min(s*p.x, s*p.y), l), abs(l)-0.03*sz);
    }
}

//////////////////////////////////////////////////////////////////////
// draw color icon (RGB or facet-shaded selectors)

void draw_color_icon(vec2 p, float sz, int i, bool enable, inout vec3 color) {
    const float k = 0.8660254037844387;
    mat2 R = mat2(-0.5, k, -k, -0.5);
    vec2 p1 = vec2(k*sz, 0);
    vec2 p2 = vec2(0, 0.5*sz);
    mat3 colors;
    if (i == 0) {
        colors = mat3(vec3(1, 0, 0),
                      vec3(1, 1, 0),
                      vec3(0, 0, 1));
    } else {
        colors = mat3(vec3(0.6, 0, 0.6),
                      vec3(0.7, 0.4, 0.7),
                      vec3(0.1, 0.5, 0.5));
    }

    float ue = enable ? 1. : 0.3;
    float ds = 1e5;

    for (int j=0; j<3; ++j) {
        vec2 ap = vec2(abs(p.x), abs(p.y-0.5*sz));
        vec2 dls = dline_seg(ap, p2, p1);
        p = R*p;
        color = mix(color, colors[j], smoothstep(1.0, 0.0, -dls.x+0.5) * ue);
        ds = min(ds, dls.y);
    }

    color = mix(color, vec3(0), smoothstep(1.0, 0.0, ds-0.05*sz) * ue);
}

//////////////////////////////////////////////////////////////////////
// draw sphere inset for bottom left corner

void draw_sphere_inset(in vec2 p, inout vec3 color) {
    float px = inset_scl;
    float dot_size = max(3.0*px, 0.03);
    float line_width = max(.25*px, 0.003);
    float lp = length((p - inset_ctr)*px);
    vec3 sp = sphere_from_gui(p);
    if (lp < 1.) {
        color = vec3(1);
        float d_tri = 1e5;
        float d_circ = 1e5;
        for (int i=0; i<3; ++i) {
            d_circ = min(d_circ, length(sp - tri_verts[i]));
            d_circ = min(d_circ, length(sp - tri_spoints[i]));
            d_tri = min(d_tri, dot(sp, tri_edges[i]));
        }
        d_circ = min(d_circ, length(sp - tri_spoints[3]));
        float d_V = length(sp - poly_vertex);
        vec3 sp2 = sp;
        tile_sphere(sp2);
        float d_gray = 1e5;

        for (int i=0; i<3; ++i) {
            d_gray = min(d_gray, abs(dot(sp2, tri_edges[i])));
        }

        float d_pink = length(sp2 - poly_vertex);

        color = mix(color, vec3(0.85), smoothstep(px, 0.0, d_gray-2.*line_width));
        color = mix(color, vec3(0.9, 0.5, 0.5), smoothstep(px, 0.0, d_pink-0.7*dot_size));
        color = mix(color, vec3(0.6), smoothstep(px, 0.0, -d_tri));
        color = mix(color, vec3(0), smoothstep(px, 0.0, abs(d_tri)-line_width));
        color = mix(color, vec3(1), step(d_circ, dot_size));
        color = mix(color, vec3(0.7, 0, 0), smoothstep(px, 0.0, d_V-dot_size));
        color = mix(color, vec3(0), smoothstep(px, 0.0, abs(d_circ - dot_size)-line_width));
    }

    color = mix(color, vec3(0), smoothstep(px, 0.0, abs(lp - 1.)-line_width));
}

//////////////////////////////////////////////////////////////////////
// was for debugging, now just for fun

vec3 stereographic_polar_diagram(in vec2 p, in vec2 theta) {
    mat3 R = rotX(-theta.x)*rotY(-theta.y);
    float rad = length(planar_verts[0]);
    float scl = 8.0*rad / iResolution.y;
    p *= scl;
    float d = 1e5;
    vec3 Rctr = R * vec3(0, 0, 1);
    vec3 Rp3d = R * vec3(p, 1);
    vec2 Rp = Rp3d.xy / Rp3d.z;

    for (int i=0; i<3; ++i) {
        vec3 tp = (tri_verts[i] * planar_proj * R);
        d = min(d, length(p - tp.xy / tp.z) - 2.*scl);
    }

    vec3 pos = sphere_from_planar(Rp) * sign(Rp3d.z);
    mat3 M = tile_sphere(pos);

    for (int i=0; i<3; ++i) {
        vec3 e =  M * tri_edges[i] * planar_proj * R;
        e /= length(e.xy);
        d = min(d, abs(dot(vec3(p, 1), e)));
    }

    vec3 pv = M * poly_vertex * planar_proj * R;
    vec3 color = vec3(1);
    if (length(Rp) < rad) {
        color = vec3(1, .5, 1);
    }

    float Mdet = dot(M[0], cross(M[1], M[2]));

    color *= mix(0.8, 1.0, step(0.0, Mdet));
    color = mix(color, vec3(0, 0, 1), smoothstep(scl, 0.0, abs(length(Rp)-rad)-.5*scl));
    color *= smoothstep(0., scl, d-0.25*scl);
    color = mix(color, vec3(0.7, 0, 0), smoothstep(scl, 0., length(p - pv.xy / pv.z)-3.*scl));

    vec3 e = vec3(0, 0, 1) * R;
    e /= length(e.xy);
    d = abs(dot(vec3(p, 1), e));
    color = mix(color, vec3(0.0, 0, 0.5), smoothstep(scl, 0., d-.5*scl));
    return color;
}

//////////////////////////////////////////////////////////////////////
// helper function for drawing icons below

void icon_dist_update(inout vec2 blk_gray,
                      float d, bool enable) {
    if (enable) {
        blk_gray.x = min(blk_gray.x, d);
    } else {
        blk_gray.y = min(blk_gray.y, d);
    }
}

//////////////////////////////////////////////////////////////////////
// our main image - apply AA to rendered polyhedron and draw GUI

void main() {
    ////////////////////////////////////////////////////////////
    // set up GUI placement and load in settings from texture A

    bary_poly_vertex = load3(BARY_COL, TARGET_ROW);
    spoint_selector = load4(SPSEL_COL, TARGET_ROW);
    vec4 theta = load4(THETA_COL, TARGET_ROW);
    setup_triangle(load3(PQR_COL, TARGET_ROW));
    vec4 decorations = load4(DECOR_COL, TARGET_ROW);
    vec4 misc = load4(MISC_COL, TARGET_ROW);
    bool is_linked = (misc.x != 0.);
    float gui = load(MISC_COL, CURRENT_ROW).z;
    setup_gui(iResolution.xy, gui);

#ifdef STEREOGRAPHIC_POLAR

    // render a cool 2D diagram
    vec3 color = stereographic_polar_diagram(gl_FragCoord.xy - object_ctr, theta.xy);
    color = mix(vec3(1), color, smoothstep(0.0, 100.0, gl_FragCoord.x-2.*inset_ctr.x));

#else

    vec3 color = texelFetch(iChannel1, ivec2(gl_FragCoord.xy), 0).xyz;

#endif
    // everything from here down is just UI and gamma correction

    vec3 pre_gui_color = color;

    draw_sphere_inset(gl_FragCoord.xy, color);

    float d_gray = 1e5;
    vec2 d_bg = vec2(1e5);

    for (int i=0; i<3; ++i) {
        vec2 text_pos = gl_FragCoord.xy - char_ui_box(i).xy;
        d_bg.x = min(d_bg.x, font2d_dist(text_pos, text_size, vec2(pqr[i], 12.0)));
        d_gray = min(d_gray, spin_icon_dist(text_pos, text_size, true, pqr[i] >= 5.));
        d_gray = min(d_gray, spin_icon_dist(text_pos, text_size, false, pqr[i] <= 2.));
        text_pos -= vec2(1, 0) * text_size;
    }

    float icon_size = 0.35*text_size;

    for (int row=0; row<2; ++row) {
        vec4 df = load4(!is_linked && row == 0 ? DFUNC0_COL : DFUNC1_COL, TARGET_ROW);

        for (int i=0; i<5; ++i) {
            vec2 p = gl_FragCoord.xy - dfunc_ui_box(i, row).xy;
            float idist = dfunc_icon_dist(p, icon_size, i);
            float dfi;
            if (i == 0) { dfi = 1. - dot(df, vec4(1)); } else { dfi = df[i-1]; }
            icon_dist_update(d_bg, idist, dfi != 0.);
        }
    }

    for (int i=0; i<4; ++i) {
        vec2 p = gl_FragCoord.xy - decor_ui_box(i).xy;
        float idist = decor_icon_dist(p, icon_size, i);
        icon_dist_update(d_bg, idist, decorations[i] != 0.);
    }

    for (int i=0; i<2; ++i) {
        vec2 p = gl_FragCoord.xy - color_ui_box(i).xy;
        bool enable = (misc.y == float(i));
        draw_color_icon(p, icon_size, i, enable, color);
    }

    float ldist = dfunc_icon_dist(gl_FragCoord.xy - link_ui_box().xy,
                                  icon_size, is_linked ? 6 : 5);
    icon_dist_update(d_bg, ldist, is_linked);
    vec4 rule_box = vec4(inset_ctr.x,
                         iResolution.y - 2.75*text_size,
                         0.19 * iResolution.y,
                         0.25);
    d_gray = min(d_gray, box_dist(gl_FragCoord.xy, rule_box));
    rule_box.y -= 2.5*text_size;
    d_gray = min(d_gray, box_dist(gl_FragCoord.xy, rule_box));
    color = mix(vec3(0), color, smoothstep(0.0, 1.0, d_bg.x));
    color = mix(vec3(0.4), color, smoothstep(0.0, 1.0, d_bg.y));
    color = mix(vec3(0.2), color, smoothstep(0.0, 1.0, d_gray));

#ifdef DEBUG_HITBOXES

    float d_hitbox = 1e5;
    d_hitbox = min(d_hitbox, length(gl_FragCoord.xy - inset_ctr) - 1./inset_scl);

    for (int i=0; i<3; ++i) {
        d_hitbox = min(d_hitbox, box_dist(gl_FragCoord.xy, tri_ui_box(i, -1.)));
        d_hitbox = min(d_hitbox, box_dist(gl_FragCoord.xy, tri_ui_box(i,  1.)));
        d_hitbox = min(d_hitbox, box_dist(gl_FragCoord.xy, char_ui_box(i)));
    }

    for (int i=0; i<5; ++i) {
        for (int row=0; row<2; ++row) {
            d_hitbox = min(d_hitbox, box_dist(gl_FragCoord.xy, dfunc_ui_box(i, row)));
        }
    }

    for (int i=0; i<4; ++i) {
        d_hitbox = min(d_hitbox, box_dist(gl_FragCoord.xy, decor_ui_box(i)));
    }

    for (int i=0; i<2; ++i) {
        d_hitbox = min(d_hitbox, box_dist(gl_FragCoord.xy, color_ui_box(i)));
    }

    d_hitbox = min(d_hitbox, box_dist(gl_FragCoord.xy, link_ui_box()));

    color = mix(vec3(1, 0, 1), color, 0.5+0.5*smoothstep(0., 1., d_hitbox));

#endif

    color = mix(pre_gui_color, color, gui);
    // gamma correction
    color = pow(color, vec3(1.0/2.2));
    fragColor = vec4(color, 1);
}
