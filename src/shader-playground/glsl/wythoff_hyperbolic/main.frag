/* Hyperbolic Wythoff explorer v2, by mattz
   License https://creativecommons.org/licenses/by-nc-sa/3.0/

   Click in the display to move the center. Shift + click to
   set rotation. All of the UI elements on the left are
   interactive.

   Keys:

     ENTER   Generate a random tiling!
     + or -  Next/prev random tiling
     SPACE   Show or hide the UI
     C       Reset center position & rotation - halt motion
     G       Toggle gyrating motion
     R       Toggle continuous rotation
     T       Toggle translation along geodesic - a little
             glitchy sometimes due to numerical inaccuracy :(
     SHIFT   Reveal central point

   These keys duplicate functionality in the UI:

     [ or ]  Previous/next projection
     1-7     Set generator point
     Q or A  Increment/decrement degree of 1st triangle vertex
     W or S  Increment/decrement degree of 2nd triangle vertex
     E or D  Increment/decrement degree of 2nd triangle vertex
     YUIOP   Draw style options
     JKL     Color schemes
     X       Fix color (forced when translating along geodesic)

   This shader is basically https://www.shadertoy.com/view/wtj3Ry
   with a few improvements:

     - using hyperboloid model instead of Poincare disk for
       "native" coordinate representation simplifies (LOL)
       code and increases numerical stability

     - added several other models/projections of the hyperbolic
       plane besides Poincare disk:

        - Upper half-plane
        - Band
        - Inverted Poincare disk
        - Orthographic projection
        - Beltrami-Klein model

     - added support for translation along geodesics

     - added support for rotation, continuous rotation mode

     - added a new coloring type: random gradients of Viridis
       see https://www.shadertoy.com/view/WlfXRN

     - added a new draw style: circle packing

     - use flat shading for rainbow/HSV coloring, looks cooler

   Have fun!
   -mattz

*/

// scene transform globals
mat2 sceneRotate;
vec3 sceneCenter;
vec3 sceneWrap;

//////////////////////////////////////////////////////////////////////
// isometries to manipulate scene

vec3 sceneTransformFwd(vec3 p) {
    p = hyperTranslate(p, sceneWrap);
    p.xy = sceneRotate * p.xy;
    p = hyperTranslate(p, sceneCenter);
    return p;
}

vec3 sceneTransformInv(vec3 p) {
    p = hyperTranslate(p, vec3(-sceneCenter.xy, sceneCenter.z));
    p.xy = p.xy * sceneRotate;
    p = hyperTranslate(p, vec3(-sceneWrap.xy, sceneWrap.z));
    return p;
}

//////////////////////////////////////////////////////////////////////
// repeated reflections of triangle till it lands on x

float flipTriangleToPoint(inout mat3 edges, in vec3 x) {

    // negative = odd, positive = even
    float parity = 1.0;

    int insideCount = 0;
    int i = 0;

    // enough flips to cover the hyperboloid hopefully
    for (int iter=0; iter<60; ++iter) {

        // test if x is inside edge i
        if (hyperDot(x, edges[i]) < 0.) {

            if (++insideCount == 3) {
                break;
            }

        } else {

            // not done yet
            insideCount = 0;

            // get indices of other two edges
            int j = TRI_NEXT(i);
            int k = TRI_LAST(i, j);

            // reflect edge j and k about edge i
            edges[j] = reflectPG(edges[j], edges[i]);
            edges[k] = reflectPG(edges[k], edges[i]);

            // flip sign on edge i
            edges[i] = -edges[i];

            // flip parity
            parity = -parity;

        } // x outside edge

        // increment test edge
        i = TRI_NEXT(i);

    } // for each flip

    return parity;

}

//////////////////////////////////////////////////////////////////////
// return integers such that x is nearest perpendicular,
// y is nearest face, and z is second-nearest face.
//
// note that y == z if the perpendicular is a mirror (i.e. lies
// on an edge incident to a right angle)

ivec3 computeFace(vec3 x, mat3 verts, vec3 generator,
                  mat3 perps, int triangleFlags) {

    // approx. distances to each perpendicular
    vec3 pdists = -hyperConj(x) * perps;

    // true unsigned distances along hyperboloid
    vec3 pdistsTrue = asinh(abs(pdists));

    // will hold return value
    ivec3 face;

    // dist to nearest perp
    float dmin = 1e5;

    // dist from cur point to generator
    float gdist = hyperDistPP(x, generator);

    // for each perp
    for (int i=0; i<3; ++i) {

        // if zero length, ignore it
        if (!QUERY_BIT(triangleFlags, BIT_PERP_HAS_LENGTH, i)) {
            continue;
        }

        // compute distance to ray from perpendicular to edge

        // get the line perpendicular to perps[i] passing thru generator
        vec3 l = geodesicPerpThruPoint(perps[i], generator);

        // if x is over that line, take distance to generator, otherwise distance to perp
        float d = hyperDot(x, l)*hyperDot(verts[i], l) > 0. ? gdist : pdistsTrue[i];

        // update dmin
        if (d < dmin) {
            dmin = d;
            face.x = i;
        }

    }

    // now face.x holds index of closest perp

    // get vertices along the edge that perp is perpendicular to
    face.y = TRI_NEXT(face.x);
    face.z = TRI_LAST(face.x, face.y);

    // if not a mirror edge...
    if (QUERY_BIT(triangleFlags, BIT_PERP_SPLITS_EDGE, face.x)) {
        // see which side of perp we lie on
        if (pdists[face.x]*hyperDot(verts[face.y], perps[face.x]) > 0.) {
            face = face.xzy;
        } else {
            face = face.xyz;
        }
    } else if (QUERY_BIT(triangleFlags, BIT_VERT_IS_FACE, face.y)) {
        // was a mirror edge so choose the only valid vertex along it
        face = face.xyy;
    } else {
        face = face.xzz;
    }

    return face;

}

//////////////////////////////////////////////////////////////////////
// from https://www.shadertoy.com/view/WlfXRN

vec3 palette(float t) {

    const vec3 c0 = vec3(0.2777273272234177, 0.005407344544966578, 0.3340998053353061);
    const vec3 c1 = vec3(0.1050930431085774, 1.404613529898575, 1.384590162594685);
    const vec3 c2 = vec3(-0.3308618287255563, 0.214847559468213, 0.09509516302823659);
    const vec3 c3 = vec3(-4.634230498983486, -5.799100973351585, -19.33244095627987);
    const vec3 c4 = vec3(6.228269936347081, 14.17993336680509, 56.69055260068105);
    const vec3 c5 = vec3(4.776384997670288, -13.74514537774601, -65.35303263337234);
    const vec3 c6 = vec3(-5.435455855934631, 4.645852612178535, 26.3124352495832);

    return c0+t*(c1+t*(c2+t*(c3+t*(c4+t*(c5+t*c6)))));

}

//////////////////////////////////////////////////////////////////////
// based on https://www.shadertoy.com/view/4sfGzS

vec2 noise( in vec3 x ) {

    vec3 p = floor(x);
    vec3 f = fract(x);
	f = f*f*(3.0-2.0*f);
	vec2 uv = (p.xy+vec2(27.0,11.0)*p.z) + f.xy;
	vec4 t = textureLod( iChannel2, (uv+0.5)/256.0, 0.0);
	return mix( t.xz, t.yw, f.z );

}

//////////////////////////////////////////////////////////////////////
// random rgb values, just to look cool

vec3 rando(vec3 x, vec3 v, vec3 vOrig, float vgmax, bool fixColors, float seed) {

    float dz = vOrig.z - 1.;

    float k = length(vOrig.xy);
    const float kmax = 1.0;

    vec2 cs = (k < kmax ? vOrig.xy : vOrig.xy*kmax/k);
    float r = dz < 1e-3 ? 0. : acosh(vOrig.z);

    vec2 scl = fixColors ? vec2(1.5, 0.2) : vec2(127, 1);

    vec2 n = noise(vec3(scl.x*cs, scl.y*r) + mod(seed, 187.));

    float theta = n.y*2.*PI;

    vec3 l = vec3(cos(theta), sin(theta), 0);

    l = hyperTranslate(l, v);

    const float margin = 0.125;
    const float basescl = 1. - 2.*margin;

    float d = hyperDistPG(x, l);
    float offset = d * margin / vgmax;

    vec3 color = palette(smoothstep(0., 1., n.x)*basescl + margin + offset);

    return color*color; // to counter sqrt in main

}

//////////////////////////////////////////////////////////////////////
// hue from color in [0, 1]

vec3 hue(float h) {
    vec3 c = mod(h*6.0 + vec3(2, 0, 4), 6.0);
	return clamp(min(c, -c+4.0), 0.0, 1.0);
}

//////////////////////////////////////////////////////////////////////
// rainbow coloring based on Poincare disk projection

vec3 rainbow(vec3 x) {
    vec2 d = diskFromHyperboloid(x);
    float h = 0.5*atan(d.x, d.y)/PI;
    vec3 rgb = hue(h);
    return mix(rgb, WHITE, 1.-dot(d.xy, d.xy));
}

//////////////////////////////////////////////////////////////////////
// for coloring tiling - each polygon gets a constant fill color

vec3 getFaceColor(vec3 x, int idx, int perpToMirror,
                  mat3 verts, mat3 perps, int style, float vgmax,
                  bool fixColors, float seed) {


    if (style == FACE_COLOR_PRIMARY) {

        // primary colors just care about index for red/blue/yellow
        return VCOLORS[idx];

    } else {

        // other colorings depend on vertex position - get vertex for this face
        vec3 v = verts[idx];

        // flip it about mirror if necessary
        if (perpToMirror >= 0) { v = reflectPG(v, perps[perpToMirror]); }

        vec3 vOrig = fixColors ? v : sceneTransformInv(v);

        if (style == FACE_COLOR_RAINBOW) {
            return rainbow(vOrig);
        } else {
            return rando(x, v, vOrig, vgmax, fixColors, seed);
        }

    }

}

//////////////////////////////////////////////////////////////////////
// construct a line from 2 points

vec3 line2D(vec2 a, vec2 b) {
    vec2 n = perp(b - a);
    return vec3(n, -dot(n, a));
}

//////////////////////////////////////////////////////////////////////
// 2D distance to line

float lineDist2D(vec3 l, vec2 p) {
    float s = length(l.xy);
    return (dot(l.xy, p) + l.z)/s;
}

//////////////////////////////////////////////////////////////////////
// 2D distance to line

float lineDist2D(vec2 a, vec2 b, vec2 p) {
    return lineDist2D(line2D(a, b), p);
}

//////////////////////////////////////////////////////////////////////
// 2D distances to line and line segment

vec2 lineSegDist2D(vec2 a, vec2 b, vec2 p) {

    p -= a;
    b -= a;

    vec2 n = normalize(perp(b));

    float u = clamp(dot(p, b)/dot(b, b), 0., 1.);

    return vec2(dot(b, n) - dot(p, n), length(p-u*b));

}

//////////////////////////////////////////////////////////////////////
// distance to character in SDF font texture

float fontDist(vec2 tpos, float size, vec2 offset) {

    float scl = 0.63/size;

    vec2 uv = tpos*scl;
    vec2 font_uv = (uv+offset+0.5)*(1.0/16.0);

    float k = texture(iChannel1, font_uv, -100.0).w + 1e-6;

    vec2 box = abs(uv)-0.5;

    return max(k-127.0/255.0, max(box.x, box.y))/scl;

}

//////////////////////////////////////////////////////////////////////
// a string is a group of 4-character chunks (last one holds str len)

float stringDist(vec2 textPos, float textSize, ivec4 chars) {


    int len = int(chars.w) >> 24;
    float flen = float(len);

    float xsize = 0.8*textSize;

    float x0 = -0.5*(flen-1.)*xsize;
    float xRel = textPos.x - x0;

    float cidx = floor(xRel/xsize + 0.5);

    if (cidx < 0. || cidx >= flen || abs(textPos.y) > textSize) {
        return 1e5;
    }

    float xChar = x0 + cidx*xsize;

    int i = int(cidx);
    int c = chars[i>>2] >> ((i&0x3)<<3);

    int lo = c & 0xF;
    int hi = (c >> 4) & 0xF;

    vec2 offset = vec2(float(lo), 15.-float(hi));

    return fontDist(textPos - vec2(xChar, 0), textSize, offset);

}

//////////////////////////////////////////////////////////////////////
// distance to triangle for spin box

float spinIconDist(vec2 pos, float size, bool flip, bool dim) {

    if (flip) { pos.y = -pos.y; }
    pos.x = abs(pos.x);

    vec2 p0 = vec2(0, 0.2)*size;
    vec2 p1 = vec2(0.35, 0.2)*size;
    vec2 p2 = vec2(0.0, -0.2)*size;

    float d = max(lineDist2D(p0, p1, pos),
                  lineDist2D(p1, p2, pos));

    if (dim) {
        d = abs(d + 0.02*pqrSize) - 0.02*size;
    }

    return d;

}

//////////////////////////////////////////////////////////////////////
// distance to decor icon

float styleIconDist(vec2 p, float sz, int style) {

    float s = sign(p.x*p.y);

    p = abs(p);

    // outside edge dist
    vec2 a = vec2(0, sz);
    vec2 b = vec2(sz, 0);
    float l = lineDist2D(a, b, p);

    if (style == STYLE_DRAW_GENERATOR) {
        float c = length( p - (p.x > p.y ? b : a)*0.8 );
        return c - 0.2*sz;
    } else if (style == STYLE_DRAW_POLYGONS) {
        return abs(l + 0.04*sz) - 0.08*sz;
    } else if (style == STYLE_DRAW_TRIANGLES) {
        return min(abs(l), max(min(p.x, p.y), l)) - 0.03*sz;
    } else if (style == STYLE_DRAW_CIRCLES) {
        float c = length(p) - 0.65*sz;
        return max(l, -c);
    } else {
        return min(max(min(s*p.x, s*p.y), l), abs(l)-0.03*sz);
    }

}

//////////////////////////////////////////////////////////////////////
// draw color icon (RGB or facet-shaded selectors)

void drawColorIcon(vec2 p, float sz, int i, bool enable, inout vec3 color) {

    const float k = 0.8660254037844387;

    mat2 R = mat2(-0.5, k, -k, -0.5);

    vec2 p1 = vec2(k*sz, 0);
    vec2 p2 = vec2(0, 0.5*sz);

    float ue = enable ? 1. : 0.3;
    float ds = 1e5;

    vec2 po = p;

    for (int j=0; j<3; ++j) {

        vec2 ap = vec2(abs(p.x), abs(p.y-0.5*sz));

        vec2 dls = lineSegDist2D(p2, p1, ap);

        vec3 src = WHITE;

        if (i == 0) {
            src = VCOLORS[j];
        } else if (i == 1) {
            float t = (atan(po.y, po.x)+0.5*PI)*0.5/PI;
            src = hue(t - 0.333) * 0.6666 + 0.3333;
        } else {
            const float k[3] = float[3](0.75, 0.25, 0.5);
            src = palette(k[j] + 0.5*dot(p-p2, perp(p2-p1))/(sz*sz) );
        }

        color = mix(color, src, smoothstep(1.0, 0.0, -dls.x+0.5) * ue);
        ds = min(ds, dls.y);

        p = R*p;

    }

    color = mix(color, vec3(0), smoothstep(1.0, 0.0, ds-0.05*sz) * ue);

}

//////////////////////////////////////////////////////////////////////
// draw helper arrow that appears under mouse

vec3 drawCompass(vec3 colorOut, vec2 uv) {

    vec2 ctrUV = fromHyperboloid(sceneCenter);

    vec3 h = hyperboloidFromOrtho(vec2(0.1, 0));

    vec2 y = normalize(fromHyperboloid(sceneTransformFwd(h.yxz)) - ctrUV);

    vec2 p = (uv - ctrUV)/px;
    p = p*mat2(-perp(y), y);

    float s = pqrSize;

    float d = fontDist(p, s, vec2(1,14));

    d = max(d, max(abs(p.y) - 0.8*s, abs(p.x) - 0.5*s));

    colorOut = mix(colorOut, BLACK, smoothstep(1.0, 0.0, d-1.5));
    colorOut = mix(colorOut, WHITE, smoothstep(1.0, 0.0, d+0.5));

    return colorOut;

}

//////////////////////////////////////////////////////////////////////

void mainImage( out vec4 fragColor, in vec2 fragCoord ) {

    ///////////////////////////////////////////////////
    // load data from registers

    vec4 pqr = LOAD4(REG_PQR_PROJ);
    vec3 gbary = LOAD3(REG_GENERATOR);
    vec4 center = LOAD4(REG_CENTER);
    ivec4 flags = ivec4(LOAD4(REG_FLAGS));
    vec3 uiState = LOAD3(REG_UI_STATE);
    vec2 rvec = LOAD2(REG_ROTATE);
    vec3 time = LOAD3(REG_TIME);
    vec4 wrap = LOAD4(REG_WRAP);

    bool paused = (time.x == time.y);

    sceneCenter = center.xyz;
    sceneWrap = vec3(0, 0, 1);
    sceneRotate = mat2(rvec, perp(rvec));

    int drawStyle = flags.x;
    int faceColor = flags.y;
    int triangleFlags = flags.z;

    ///////////////////////////////////////////////////
	// set up projection and draw tiling if valid

    setupProjection(int(pqr.w), iResolution.xy, uiState.x);

    vec2 uv = sceneFromFrag(fragCoord);

    vec3 colorOut = WHITE;
    vec3 uiColor = WHITE;

    float uiOpacity = smoothstep(0.0, 0.9, uiState.x);

    bool insideUI = insideBox(fragCoord, uiBox) && uiOpacity > 0.;
    bool insideInset = insideUI && insideBox(fragCoord, insetBox);
    bool drawTiling = pointValid(uv) && (!insideUI|| uiOpacity < 1.);

    // compute edges from PQR
    mat3 edges;

    if (insideInset || drawTiling) {
        edges = setupTriangle(pqr.xyz);
        insetEdges = edges;
    }

    bool fixColors = ((center.w == CENTER_SWEEPING) ||
                      bool(flags.x & STYLE_FIX_COLOR));

    // draw tiling
    if (drawTiling) {

        ///////////////////////////////////////////////////
        // handle scroll

        // see if scroll pos stored as hyperboloid coords or
        // scene coords (latter need projection)
        if (sceneCenter.z == 0.) {
            sceneCenter = toHyperboloid(projValid(sceneCenter.xy, false));
        }

        vec2 ctrScene = fromHyperboloid(sceneCenter);

        // deal with wrap
        if (center.w == CENTER_SWEEPING) {

            float dist = wrap.w;

            vec3 u = vec3(0, 0, 1);

            dist *= fract(time.z) - 0.5;

            sceneWrap = hyperNormalizeP(u*cosh(dist) + wrap.xyz*sinh(dist));

        }

        ///////////////////////////////////////////////////
        // triangle setup

        // translate edges by scroll position
        for (int i=0; i<3; ++i) {
            edges[i] = sceneTransformFwd(edges[i]);
        }

        // project current frag pos to the hyperboloid
        vec3 x = toHyperboloid(uv);

        x = toHyperboloid(fromHyperboloid(x));

        // flip triangle on top of current frag pos
        float parity = flipTriangleToPoint(edges, x);

        // compute vertices
        mat3 verts = hyperTriVerts(edges);

        // compute generator position from barycentric coords
        vec3 generator = hyperNormalizeP(verts * gbary);

        // compute perpendiculars thru generator to edges
        mat3 perps = hyperTriPerps(edges, generator);

        // compute max dist to vert from generator
        float vgmax = -1e5;

        for (int i=0; i<3; ++i) {
            vgmax = max(vgmax, hyperDistPP(verts[i], generator));
        }

        // compute radii for drawing circles below
        vec3 rads = vec3(1e5);

        if (bool(drawStyle & STYLE_DRAW_CIRCLES)) {
            for (int i=0; i<3; ++i) {
                if (QUERY_BIT(triangleFlags, BIT_VERT_IS_FACE, i)) {
                    int j = TRI_NEXT(i);
                    int k = TRI_LAST(i, j);
                    rads[i] = min(rads[i], abs(hyperDot(verts[i], perps[j])));
                    rads[i] = min(rads[i], abs(hyperDot(verts[i], perps[k])));
                }
            }
            rads = asinh(rads);
        }

        /////////////////////////////////////////////////////////////////
        // find out which polygon face we lie on

        // face.x = closest perp
        // face.y = closest vert index
        // face.z = second closest vert index

        ivec3 face = computeFace(x, verts, generator, perps, triangleFlags);

        float fparity = hyperDot(verts[face.y], perps[face.x]) < 0. ? -1. : 1.;

        int perpToMirror = face.z == face.y ? face.x : -1;

        // colors for each face
        vec3 faceFG = getFaceColor(x, face.y, -1,
                                   verts, perps, faceColor, vgmax,
                                   fixColors, uiState.z);

        vec3 faceBG = getFaceColor(x, face.z, perpToMirror,
                                   verts, perps, faceColor, vgmax,
                                   fixColors, uiState.z);

        /////////////////////////////////////////////////////////////////
        // shade the current pixel

        vec3 accum = vec3(0);
        vec2 origUV = uv;

        // 4-Rook Antialiasing
        // https://blog.demofox.org/2015/04/23/4-rook-antialiasing-rgss/
        const vec2 deltas[4] = vec2[4](
            vec2(0.125, 0.375),
            vec2(-0.375, 0.125),
            vec2(0.375, -0.125),
            vec2(-0.125, -0.375)
        );

        // we will do either 1 or 4 subpixels - only need to
        // worry about AA if projection is not conformal
        float subPixelCoverage = isConformal ? 1.0 : 0.5;
        float subPixelWeight = subPixelCoverage * subPixelCoverage;
        float subPixelOffset = isConformal ? 0.0 : px;

        // antialiasing distance
        float lengthScale = metric(uv)/(px*subPixelCoverage);

        // shade up to 4 sub-pixels
        for (int i=0; i<4; ++i) {

            // sub-pixel offset
            uv = origUV + subPixelOffset * deltas[i];

            // project
            x = toHyperboloid(uv);

            // dists to triangle edges
            vec3 edists = -hyperConj(x) * edges;
            float emin = min(edists[0], min(edists[1], edists[2]));

            // dist to polygon edges/perps
            float pmin = fparity*hyperDot(x, perps[face.x]);

            // shade fg vs BG
            float fgWeight = smoothstep(-0.5, 0.5, pmin*lengthScale*0.5);

            vec3 subPixelColor = mix(faceBG, faceFG, fgWeight);

            // shade triangles
            if (bool(drawStyle & STYLE_SHADE_TRIANGLES)) {
                float brightWeight = smoothstep(-0.5, 0.5, parity*emin*lengthScale);
                subPixelColor *= mix(0.75, 1.0, brightWeight);
            }

            // draw triangle outlines
            if (bool(drawStyle & STYLE_DRAW_TRIANGLES)) {
                float tWeight = smoothstep(0.0, 1.0, (emin - 0.5*lineSize)*lengthScale);
                subPixelColor *= mix(0.33333, 1.0, tWeight);
            }

            // draw polygon edges, generator, and circles
            float bdist = 1e5;

            if (bool(drawStyle & STYLE_DRAW_POLYGONS)) {
                bdist = min(bdist, abs(pmin) - lineSize);
            }

            if (bool(drawStyle & STYLE_DRAW_GENERATOR)) {
                bdist = min(bdist, hyperDistPP(x, generator)- 4.*lineSize);
            }

            if (bool(drawStyle & STYLE_DRAW_CIRCLES)) {
                float cmin = 1e5;
                for (int i=0; i<3; ++i) {
                    if (QUERY_BIT(triangleFlags, BIT_VERT_IS_FACE, i)) {
                        float cdist = (hyperDistPP(x, verts[i])-rads[i]);
                        cmin = min(cmin, cdist);
                    }
                }
                bdist = min(bdist, -cmin);
            }

            // shade in black
            subPixelColor *= smoothstep(0.0, 1.0, bdist*lengthScale);

            // accumulate this subpixel
            accum += subPixelWeight * subPixelColor;

            // only need to do one sample for conformal maps (AA just for klein & ortho)
            if (isConformal) { break; }

        }

        // done with tiling
        colorOut = accum;

        // compass for locating center & direction
        if (bool(flags.w)) {
            sceneWrap = vec3(0, 0, 1);
            colorOut = drawCompass(colorOut, uv);
        }

    }

    // draw UI
    if (insideUI) {

        float dBlack = 1e5;
        float dGray = 1e5;

        // text and spin icons
        for (int i=0; i<3; ++i) {

            vec2 textPos = fragCoord.xy - digitUIBox(i).xy;
            dBlack = min(dBlack, fontDist(textPos, pqrSize, vec2(pqr[i], 12.0)));

            vec2 p0 = fragCoord.xy - triUIBox(i, 1.).xy;
            vec2 p1 = fragCoord.xy - triUIBox(i, -1.).xy;
            dGray = min(dGray, spinIconDist(p0, pqrSize, true, pqr[i] == PQR_MAX));
            dGray = min(dGray, spinIconDist(p1, pqrSize, false, pqr[i] == PQR_MIN));

        }

        // top row of clickable icons
        for (int i=0; i<5; ++i) {

            int flag = (1 << i);

            vec2 p = fragCoord - iconUIBox(ivec2(i, 0)).xy;
            float idist = styleIconDist(p, iconSize, flag);

            if (bool(drawStyle & flag)) {
                dBlack = min(dBlack, idist);
            } else {
                dGray = min(dGray, idist);
            }

        }

        // bottom row of clickable icons
        for (int i=0; i<3; ++i) {
            bool enable = (faceColor == i);
            vec2 pos = iconUIBox(ivec2(i+1, 1)).xy;
            if (i > 0 && enable) {
                //float d = length(fragCoord - pos) - 1.25*iconSize;
                float d = boxDist(fragCoord, vec4(pos, vec2(1.25*iconSize)));
                float w = smoothstep(1., 0., d);
                if (center.w == CENTER_SWEEPING) {
                    uiColor = mix(uiColor, LIGHTGRAY, w);
                } else if (bool(flags.x & STYLE_FIX_COLOR)) {
                    uiColor = mix(uiColor, GRAY, w);
                }
            }
            drawColorIcon(fragCoord - pos, iconSize, i, enable, uiColor);
        }

        // projection text
        const ivec4 PROJ_STRINGS[6] = ivec4[6](
            ivec4(0x6e696f50,0xe9726163,0x73696420,0x0d00006b),
            ivec4(0x666c6148,0x616c702d,0x0000656e,0x0a000000),
            ivec4(0x646e6142,0x00000000,0x00000000,0x04000000),
            ivec4(0x65766e49,0x64657472,0x73696420,0x0d00006b),
            ivec4(0x6874724f,0x6172676f,0x63696870,0x0c000000),
            ivec4(0x746c6542,0x696d6172,0x656c4b2d,0x0e006e69)
        );

        float textDist = stringDist(fragCoord - projBox.xy,
                                    projSize,
                                    PROJ_STRINGS[activeProj]);

        // spin icons for projection
        for (int i=0; i<2; ++i) {
            vec2 p = projUIBox(i == 0 ? -1. : 1.).xy;
            p = fragCoord - p;
            p = p.yx;
            dGray = min(dGray, spinIconDist(p, 2.*projSize, i==1, false));
        }

        // inset triangle
        if (insideInset) {

            setupInset(insetEdges);
            vec2 uv = diskFromInset(fragCoord);

            if (dot(uv, uv) < 0.99) {

                vec3 x = hyperboloidFromDisk(uv);
                float ds = diskMetric(uv);

                // distance to
                float pmin = 1e5;
                float pmax = -1e5;

                float gmin = 1e5;

                for (int i=0; i<3; ++i) {
                    float di = hyperDot(x, insetEdges[i]);
                    pmin = min(pmin, abs(di));
                    pmax = max(pmax, di);
                    vec3 l = geodesicPerpThruPoint(insetBisectors[i], insetVerts[i]);
                    pmax = max(pmax, -hyperDot(x, l));
                    gmin = min(gmin, length(uv - diskFromHyperboloid(insetVerts[i])));
                    gmin = min(gmin, length(uv - diskFromHyperboloid(insetEdgePoints[i])));

                }
                gmin = min(gmin, length(uv));

                uiColor = mix(uiColor, LIGHTGRAY, step(pmax, 0.0));
                uiColor *= smoothstep(0.0, 1.0, max(pmin, pmax)*ds/insetPx-0.5);
                uiColor *= smoothstep(0.0, 1.0, gmin/insetPx-insetPointSize);
                uiColor = mix(uiColor, WHITE, smoothstep(1.0, 0.0, gmin/insetPx-insetPointSize+2.0));

                vec3 generator = hyperNormalizeP(insetVerts * gbary.xyz);
                gmin = length(uv - diskFromHyperboloid(generator));

                uiColor = mix(uiColor, RED, smoothstep(1.0, 0.0, gmin/insetPx-insetPointSize+1.75));

            }

        }

        dBlack = min(dBlack, textDist+0.25);

        // draw the things
        uiColor = mix(GRAY, uiColor, smoothstep(0.0, 1.0, dGray));
        uiColor = mix(BLACK, uiColor, smoothstep(0.0, 1.0, dBlack));

        colorOut = mix(colorOut, uiColor, uiOpacity);

    }

    // draw outer disk for klein or poincare disk
    if (shouldDrawDisk) {
        colorOut *= smoothstep(0.0, 1.0, abs(length(uv)-1.0)/px-0.5);
    }

    // draw line separating UI from scene
    if (activeProj != PROJ_DISK && activeProj != PROJ_KLEIN) {
        float lineDist = abs(lineDist2D(uiBorder, fragCoord))-0.5;
        vec3 lineColor = colorOut * smoothstep(0.0, 1.0, lineDist);
        colorOut = mix(colorOut, lineColor, uiOpacity);
    }

#ifdef DEMO_SHOW_SEED
    {
        int seed = int(uiState.z);
        bool done = false;
        float s = pqrSize;
        vec2 textPos = fragCoord - vec2(iResolution.x - 0.5*s, 0.75*s);
        for (int i=0; i<20; ++i) {
            int k = (seed % 10);
            seed = seed / 10;
            float d = fontDist(textPos, s, vec2(float(k), 12));
            colorOut = mix(colorOut, BLACK, smoothstep(1.0, 0.0, d-1.5));
            colorOut = mix(colorOut, WHITE, smoothstep(1.0, 0.0, d+1.5));
            textPos.x += 0.8*s;
            if (i > 0 && seed == 0) { break; }
        }
    }
#endif

    // approximate gamma correction
    fragColor = vec4(sqrt(colorOut), 1);

}

void main()
{
    mainImage(fragColor, gl_FragCoord.xy);
}
