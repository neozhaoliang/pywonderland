#define STORE(reg, value) if(fc == (reg)) { data = (value); }

#define STORE1(reg, value) STORE(reg, vec4(value, 0, 0, 0))
#define STORE2(reg, value) STORE(reg, vec4(value, 0, 0))
#define STORE3(reg, value) STORE(reg, vec4(value, 0))
#define STORE4(reg, value) STORE(reg, value)

#define KEY_TEX(key, row) (texelFetch(iChannel1, ivec2(key, row), 0).x != 0.)
#define KEY_IS_DOWN(key)  KEY_TEX(key, 0)
#define KEY_HIT(key)      KEY_TEX(key, 1)
#define KEY_TOGGLE(key)   KEY_TEX(key, 0)

#define MOUSE_INACTIVE       0.
#define MOUSE_SCROLL         1.
#define MOUSE_ROTATE         2.
#define MOUSE_SET_GENERATOR  3.
#define MOUSE_SNAP_GENERATOR 4.

// global variables for register storage management
vec4 data;
ivec2 fc;

//////////////////////////////////////////////////////////////////////
// return true if (1/p + 1/q + 1/r) < 1

bool isValidPQR(vec3 pqr) {
    return (pqr.x*pqr.y + pqr.x*pqr.z + pqr.y*pqr.z) < pqr.x*pqr.y*pqr.z;
}

// ensure valid pqr by modifying other axis
vec3 fixPQR(vec3 pqr, int pqrAxis) {
    for (int iter=0; iter<10; ++iter) {
        if (isValidPQR(pqr.xyz)) { break; }
        int j = TRI_NEXT(pqrAxis);
        int k = TRI_LAST(pqrAxis, j);
        if (pqr[j] > pqr[k]) { j = k; }
        pqr[j] += 1.;
    }
    return pqr;
}

//////////////////////////////////////////////////////////////////////
// compute properties of triangle whenever triangle changed

int computeTriangleFlags(mat3 edges, mat3 verts, vec3 gbary) {

    vec3 generator = hyperNormalizeP(verts * gbary);

    mat3 perps = hyperTriPerps(edges, generator);

    const float TOL = 1e-3;

    // initially:
    //   - all verts are faces,
    //   - all perps have length
    //   - all perps split edges
    int drawFlags = 0xfff;

    for (int i=0; i<3; ++i) {

        int j = TRI_NEXT(i);
        int k = TRI_LAST(i, j);

        // if generator lives on edge i, perp i has no length
        if (abs(hyperDot(generator, edges[i])) < TOL) {
            CLEAR_BIT(drawFlags, BIT_PERP_HAS_LENGTH, i);
        }

        // if vertex j or k is on perp i, it can't be a face center,
        // and perp i does not split edge i
        if (abs(hyperDot(verts[j], perps[i])) < TOL) {
            CLEAR_BIT(drawFlags, BIT_VERT_IS_FACE, j);
            CLEAR_BIT(drawFlags, BIT_PERP_SPLITS_EDGE, i);
        }

        if (abs(hyperDot(verts[k], perps[i])) < TOL) {
            CLEAR_BIT(drawFlags, BIT_VERT_IS_FACE, k);
            CLEAR_BIT(drawFlags, BIT_PERP_SPLITS_EDGE, i);
        }

    }

    return drawFlags;

}

// from https://www.shadertoy.com/view/4djSRW
vec4 hash41(float p) {
	vec4 p4 = fract(vec4(p) * vec4(.1031, .1030, .0973, .1099));
    p4 += dot(p4, p4.wzxy+19.19);
    return fract((p4.xxyz+p4.yzzw)*p4.zywx);
}

//////////////////////////////////////////////////////////////////////
// update storage registers

void mainImage( out vec4 fragColor, in vec2 fragCoord ) {

    // get integer frag coords and texel data from last frame
    fc = ivec2(fragCoord);
    data = texelFetch(iChannel0, fc, 0);

    // load all the important variables
    vec4 pqr = LOAD4(REG_PQR_PROJ);        // p, q, r, projection
    vec4 generator = LOAD4(REG_GENERATOR); // generator barycentric coordinates
    vec4 mstate = LOAD4(REG_MOUSE);        // mouse x, y, state, down
    ivec4 flags = ivec4(LOAD4(REG_FLAGS)); // style flags, face coloring, triangle flags
    vec4 center = LOAD4(REG_CENTER);       // scroll point, scroll mode
    vec4 time = LOAD4(REG_TIME);           // last time, cur time, scroll time, period
    vec3 uiState = LOAD3(REG_UI_STATE);    // current, target, start time
    vec2 rvec = LOAD2(REG_ROTATE);
    vec4 wrap = LOAD4(REG_WRAP);

    bool randomDemo = false;
    bool updateTriangle = false;

    // initialize on first frame
    if (pqr == vec4(0)) {
        randomDemo = true;
#ifndef DEMO_MODE
        uiState = vec3(1, 1, 0);
#endif
#ifdef DEMO_SEED
        uiState.z = float(DEMO_SEED);
#else
        uiState.z = floor(iDate.w * 100.);
#endif
    }

    if (KEY_HIT(187) || KEY_HIT(13)) {
        uiState.z += 1.; randomDemo = true;
    }

    if (KEY_HIT(189)) {
        uiState.z -= 1.; randomDemo = true;
    }

    if (randomDemo) {

        float s = uiState.z;

        vec4 t0 = hash41(s);
        vec4 t1 = hash41(s+1.);
        vec4 t2 = hash41(s+2.);
        vec4 t3 = hash41(s+3.);

        pqr = floor(0.999*t0 * vec4(7,1,2,NUM_PROJ)) + vec4(3,2,3,0);

        for (int i=0; i<3; ++i) { pqr.xyz = fixPQR(pqr.xyz, i); }

        vec4 r = floor(0.999*t1 * vec4(31,3,3,6));

        if (r.w == 0.) {
            pqr = pqr.zxyw;
        } else if (r.w == 1.) {
            pqr = pqr.zyxw;
        } else if (r.w == 2.) {
            pqr = pqr.yxzw;
        } else if (r.w == 3.) {
            pqr = pqr.yzxw;
        } else if (r.w == 4.) {
            pqr = pqr.xzyw;
        }

        flags.x = int(r.x);
        flags.y = int(r.y);

        if (bool(flags.x & STYLE_DRAW_CIRCLES) &&
            bool(flags.x & (STYLE_DRAW_POLYGONS | STYLE_DRAW_GENERATOR))) {
            if (t3.y > 0.5) {
                flags.x &= ~(STYLE_DRAW_POLYGONS | STYLE_DRAW_GENERATOR);
            } else {
                flags.x &= ~(STYLE_DRAW_CIRCLES);
            }
        } else if (flags.x == STYLE_DRAW_GENERATOR) {
            flags.x |= STYLE_SHADE_TRIANGLES;
        } else if (flags.x == 0 && flags.y == FACE_COLOR_PRIMARY) {
            flags.y = FACE_COLOR_RANDOM;
        }

        if (t3.z < 0.4) {
            flags.x |= STYLE_FIX_COLOR;
        }

#ifdef DEMO_MODE
        time.w = 1.0/6.0;
#else
        time.w = 1.0 / (t3.w*4. + 6.);
#endif

        generator.w = floor(0.999*t3.x*7.);

        updateTriangle = true;

        setupProjection(int(pqr.w), iResolution.xy, uiState.x);

        vec2 f = (t2.xy * 2. - 1.);
        center.xy = sceneFromFrag(sceneBox.xy + f*sceneBox.zw);
        float cc = dot(center.xy, center.xy);

        if (activeProj == PROJ_DISK || activeProj == PROJ_KLEIN) {
            if (cc > 1.) {
                center.xy /= cc;
            }
        } else if (activeProj == PROJ_INV_DISK) {
            if (cc < 1.) {
                center.xy /= cc;
            }
        }

        center.z = 0.;
        center.w = r.z + 1.;

        rvec = normalize(t2.zw);

    } else {

        // set up scene <-> frag projection
        setupProjection(int(pqr.w), iResolution.xy, uiState.x);

    }

    // update time (for pause detection)
    time.x = time.y;
    time.y = iTime;

    // see https://www.shadertoy.com/view/XdtyWB for explanation of this
    bool paused = (time.x == iTime);

#ifdef DEMO_MODE
    time.z = iTime*time.w;
#else
    if (!paused) { time.z += iTimeDelta*time.w; }
#endif

    //////////////////////////////////////////////////
    // UI/mouse interaction

    // fpr changing PQR
    int pqrAxis = -1;
    float pqrDelta = 0.;

    // Q/A, W/S, E/D
    if (KEY_HIT(81)) { pqrAxis = 0; pqrDelta =  1.; }
    if (KEY_HIT(65)) { pqrAxis = 0; pqrDelta = -1.; }
    if (KEY_HIT(87)) { pqrAxis = 1; pqrDelta =  1.; }
    if (KEY_HIT(83)) { pqrAxis = 1; pqrDelta = -1.; }
    if (KEY_HIT(69)) { pqrAxis = 2; pqrDelta =  1.; }
    if (KEY_HIT(68)) { pqrAxis = 2; pqrDelta = -1.; }

    // for changing projection
    float projDelta = 0.;

    // [/]
    if (KEY_HIT(219)) { projDelta = -1.; }
    if (KEY_HIT(221)) { projDelta =  1.; }

    // space toggles UI
    if (KEY_HIT(32)) { uiState.y = 1. - uiState.y; }

    // YUIOP
    if (KEY_HIT(89)) { flags.x ^= STYLE_DRAW_POLYGONS; }
    if (KEY_HIT(85)) { flags.x ^= STYLE_DRAW_GENERATOR; }
    if (KEY_HIT(73)) { flags.x ^= STYLE_DRAW_TRIANGLES; }
    if (KEY_HIT(79)) { flags.x ^= STYLE_DRAW_CIRCLES; }
    if (KEY_HIT(80)) { flags.x ^= STYLE_SHADE_TRIANGLES; }

    // JKL
    if (KEY_HIT(74)) { flags.y = FACE_COLOR_PRIMARY; }
    if (KEY_HIT(75)) { flags.y = FACE_COLOR_RAINBOW; }
    if (KEY_HIT(76)) { flags.y = FACE_COLOR_RANDOM; }

    // X
    if (KEY_HIT(88) && center.w != CENTER_SWEEPING) {
        flags.x ^= STYLE_FIX_COLOR;
    }

    // keys 1-7 update generator position
    for (int i=0; i<7; ++i) {
        if (KEY_HIT(49 + i)) { generator.w = float(i); updateTriangle = true; }
    }

    // is mouse down, are we clicking?
    bool mouseIsDown = min(iMouse.z, iMouse.w) > 0.;
    bool click = mouseIsDown && mstate.w == MOUSE_INACTIVE;;

    mstate = mouseIsDown ? vec4(mstate.xyz, 1) : vec4(0);

    bool shiftIsPressed = KEY_IS_DOWN(16);

    // handle initial mouse down
    if (click) {

        if (insideBox(iMouse.xy, sceneBox)) {
            if (!shiftIsPressed) {
                // scroll scene
                mstate.z = MOUSE_SCROLL;
            } else if (pointValid(sceneFromFrag(iMouse.xy))) {
                mstate.z = MOUSE_ROTATE;
            }

        } else if (insideBox(iMouse.xy, insetBox)) {
            // choose generator point
            mstate.z = MOUSE_SET_GENERATOR;
        } else if (insideBox(iMouse.xy, projUIBox(1.))) {
            // proj left/right spin
            projDelta = 1.;
        } else if (insideBox(iMouse.xy, projUIBox(-1.))) {
            // proj left/right spin
            projDelta = -1.;
        }

        // PQR spin boxes
        for (int i=0; i<3; ++i) {
            for (float delta=-1.; delta<2.; delta+=2.) {
                if (insideBox(iMouse.xy, triUIBox(i, delta))) {
                    pqrAxis = i;
                    pqrDelta = delta;
                }
            }
        }

        // draw style
        for (int i=0; i<5; ++i) {
            if (insideBox(iMouse.xy, iconUIBox(ivec2(i, 0)))) {
                flags.x ^= (1 << i);
            }
        }

        // color
        for (int i=0; i<3; ++i) {
            if (insideBox(iMouse.xy, iconUIBox(ivec2(i+1, 1)))) {
                if (i > 0 && center.w != CENTER_SWEEPING) {
                    if (flags.y == i) {
                        flags.x ^= STYLE_FIX_COLOR;
                    } else {
                        flags.x &= ~STYLE_FIX_COLOR;
                    }
                }
                flags.y = i;
            }
        }

    }

    // handle scroll using mouse
    if (mstate.z == MOUSE_SCROLL) {
        center = vec4(sceneFromFrag(iMouse.xy), 0,
                      center.w == CENTER_GYRATING ? CENTER_STATIONARY : center.w);
    }

    // handle mouse rotation
    if (mstate.z == MOUSE_ROTATE) {

        vec3 u = center.z == 0. ? toHyperboloid(projValid(center.xy, false)) : center.xyz;
        vec3 v = toHyperboloid(projValid(sceneFromFrag(iMouse.xy), true));

        vec3 l = geodesicFromPoints(u, v);
        float cosTheta = -hyperDot(l, hyperTranslate(vec3(1, 0, 0), u));
        float sinTheta = -hyperDot(l, hyperTranslate(vec3(0, 1, 0), u));

        rvec = normalize(vec2(cosTheta, sinTheta));

        if (center.w == CENTER_ROTATING) { center.w = CENTER_STATIONARY; }

    }

    // does this register need to pay attention to triangle updates?
    bool isUpdatable = (fc == REG_MOUSE || fc == REG_GENERATOR ||
                        fc == REG_FLAGS || fc == REG_WRAP);

    // if dragging generator and updatable
    if (mstate.z >= MOUSE_SET_GENERATOR && isUpdatable) {

        // setup inset triangle
        mat3 edges = setupTriangle(pqr.xyz);
        setupInset(edges);

        // get point in Poincare disk
        vec2 uv = diskProjValid(diskFromInset(iMouse.xy - mstate.xy), false);

        float SNAP_TOL = insetPointSize*2.0;
        const float MOVE_TOL = 4.;

        if (click) {

            // origin is first point
            vec4 mousePoint = vec4(uv, length(uv), 6.);

            // check all 3 verts and all 3 edge points
            for (int j=0; j<2; ++j) {
                for (int i=0; i<3; ++i) {
                    vec3 xi = j == 0 ? insetVerts[i] : insetEdgePoints[i];
                    vec2 di = uv - diskFromHyperboloid(xi) ;
                    float l = length(di);
                    vec4 p = vec4(di, l, float(i+3*j));
                    mousePoint = p.z < mousePoint.z ? p : mousePoint;
                }
            }

            // see if we shouls snap to point
            if (mousePoint.z < SNAP_TOL*insetPx) {
                generator.w = mousePoint.w;
                mstate.xy = mousePoint.xy / insetPx;
                mstate.z = MOUSE_SNAP_GENERATOR;
            }

        } else if (mstate.z == MOUSE_SNAP_GENERATOR &&
                   length(iMouse.xy - iMouse.zw) > MOVE_TOL) {
            // see if we should stop snapping
            mstate.z = MOUSE_SET_GENERATOR;
        }

        // if not snapped, solve for barycentric coords
        if (mstate.z == MOUSE_SET_GENERATOR) {

            vec3 x = hyperboloidFromDisk(uv);

            generator.xyz = inverse(insetVerts) * x;
            generator.w = -1.;

            generator.xyz /= dot(generator.xyz, vec3(1));
            generator.xyz = clamp(generator.xyz, 0., 1.);

        }

        updateTriangle = true;

    }

    // handle showing/hiding UI
    if (paused) {
        uiState.x = uiState.y;
    } else {
        uiState.x = mix(uiState.x, uiState.y, 0.08);
        if (abs(uiState.x - uiState.y) < 0.01) { uiState.x = uiState.y; }
    }

    //////////////////////////////////////////////////
    // handle changes to P, Q, R

    if (pqrDelta != 0.) {
        pqr[pqrAxis] = clamp(pqr[pqrAxis] + pqrDelta, PQR_MIN, PQR_MAX);
        pqr.xyz = fixPQR(pqr.xyz, pqrAxis);
        updateTriangle = true;
    }

    //////////////////////////////////////////////////
    // handle changes to projection

    if (projDelta != 0.) {

        vec2 f = fragFromScene(center.xy);

        pqr.w = mod(pqr.w + projDelta, NUM_PROJ);

        setupProjection(int(pqr.w), iResolution.xy, uiState.x);

        if (center.z == 0.) {
            center.xy = sceneFromFrag(f);
        }

    }

    //////////////////////////////////////////////////
    // do triangle updates if necessary

    if (updateTriangle && isUpdatable) {

        mat3 edges = setupTriangle(pqr.xyz);
        mat3 verts = hyperTriVerts(edges);
        mat3 bisectors = hyperTriAngleBisectors(edges);
        mat3 vinv = inverse(verts);

        int i = int(generator.w);

        if (i >= 0 && i < 3) {
            generator.xyz = vec3(0);
            generator[i] = 1.;
        } else if (i >= 3 && i < 6) {
            i -= 3;
            generator.xyz = vinv * intersectGG(bisectors[i], edges[i]);
        } else if (i == 6) {
            generator.xyz = vinv * intersectGG(bisectors[0], bisectors[1]);
        }

        flags.z = computeTriangleFlags(edges, verts, generator.xyz);

        vec3 edgeLengths;

        for (int i=0; i<3; ++i) {
            int j = TRI_NEXT(i);
            int k = TRI_LAST(i, j);
            edgeLengths[i] = hyperDistPP(verts[j], verts[k]);
        }

        const vec3 tbl[8] = vec3[8](
            vec3(0, 0, 2),
            vec3(0, 2, 2),
            vec3(2, 0, 2),
            vec3(2, 2, 2),
            vec3(0, 0, 2),
            vec3(2, 2, 2),
            vec3(2, 2, 2),
            vec3(1, 1, 1)
        );

        ivec3 bits = ((ivec3(pqr) & 0x1) << ivec3(0, 1, 2));
        int idx = bits.x | bits.y | bits.z;

        vec3 u = verts[0];
        vec3 v = verts[1];

        vec3 w = v + hyperDot(u, v)*u;

        w = hyperNormalizeG(w);

        float dist = dot(edgeLengths, tbl[idx]);

        wrap = vec4(w, dist);

    }

    //////////////////////////////////////////////////
    // deal with scrolling/rotation

    flags.w = int(shiftIsPressed || mstate.z == MOUSE_SCROLL);

    // C centers
    if (KEY_IS_DOWN(67)) {
        vec2 f = sceneBox.xy;
        center = vec4(sceneFromFrag(f), 0, CENTER_STATIONARY);
        rvec = vec2(1, 0);
        flags.w = 1;
    }

    // G toggles gyration
    if (KEY_HIT(71)) {
        center.w = (center.w == CENTER_GYRATING) ? CENTER_STATIONARY : CENTER_GYRATING;
    }

    // T toggles translation along triangle
    if (KEY_HIT(84)) {
        center.w = (center.w == CENTER_SWEEPING) ? CENTER_STATIONARY : CENTER_SWEEPING;
    }

    // R toggles continuous rotation
    if (KEY_HIT(82)) {
        center.w = (center.w == CENTER_ROTATING) ? CENTER_STATIONARY : CENTER_ROTATING;
    }

    // if we are moving, then update scroll pos or rotation
    if (center.w == CENTER_GYRATING) {
        float t = time.z * 2.*PI;
        float r = 1.33;
        center.xyz = hyperboloidFromOrtho(r*vec2(cos(t), sin(t)));
    } else if (center.w == CENTER_ROTATING) {
        float t = time.z * 2.*PI;
        rvec = vec2(cos(t), sin(t));
    }

    //////////////////////////////////////////////////
    // store data

    STORE4(REG_PQR_PROJ, pqr);
    STORE4(REG_GENERATOR, generator);
    STORE4(REG_MOUSE, mstate);
    STORE4(REG_FLAGS, vec4(flags));
    STORE4(REG_CENTER, center);
    STORE4(REG_TIME, time);
    STORE3(REG_UI_STATE, uiState);
    STORE2(REG_ROTATE, rvec);
    STORE4(REG_WRAP, wrap);

    // write to texture
    fragColor = data;

}

void main()
{
    mainImage(fragColor, gl_FragCoord.xy);
}
