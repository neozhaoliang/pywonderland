uniform int    latticeType;
uniform vec4   T;
uniform bool   dual;
uniform bool   snub;

// --------------------------------------------------------
// below are some configs you can tweak with
//----------------------------------------------------------

// use another color style?
#define GOLD_STYLE

// I found that in snub and some dual scenes octagoanl edges not working correctly,
// and I can't figure out why, so use cylinder shape if you want
// #define use_cylinder

// The duals of snub honeycombs are not implemented, hence if both dual and snub are defined
// only the snub type is shown.
// render the snub honeycomb?
// #define snub

// render the dual honeycomb?
// #define dual

// size of the tubes.
float tbsize = 0.06;

//----------------------------------------------------------

// initial vertex
vec3 v0;

// reflection mirrors and its inverse matrix
mat4 M, M_inv;

// vertices of the fundamental tetrahedron
mat4x3 V;

// mirror image of v0 about the tetrahedron faces
mat4x3 E;

// objects id
vec3 objIDs;

float glow;

vec3 spts[12];


#define FAR     80.
#define PI      3.141592654

mat4 inverse(mat4 m) {
  float
      a00 = m[0][0], a01 = m[0][1], a02 = m[0][2], a03 = m[0][3],
      a10 = m[1][0], a11 = m[1][1], a12 = m[1][2], a13 = m[1][3],
      a20 = m[2][0], a21 = m[2][1], a22 = m[2][2], a23 = m[2][3],
      a30 = m[3][0], a31 = m[3][1], a32 = m[3][2], a33 = m[3][3],

      b00 = a00 * a11 - a01 * a10,
      b01 = a00 * a12 - a02 * a10,
      b02 = a00 * a13 - a03 * a10,
      b03 = a01 * a12 - a02 * a11,
      b04 = a01 * a13 - a03 * a11,
      b05 = a02 * a13 - a03 * a12,
      b06 = a20 * a31 - a21 * a30,
      b07 = a20 * a32 - a22 * a30,
      b08 = a20 * a33 - a23 * a30,
      b09 = a21 * a32 - a22 * a31,
      b10 = a21 * a33 - a23 * a31,
      b11 = a22 * a33 - a23 * a32,

      det = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06;

  return mat4(
      a11 * b11 - a12 * b10 + a13 * b09,
      a02 * b10 - a01 * b11 - a03 * b09,
      a31 * b05 - a32 * b04 + a33 * b03,
      a22 * b04 - a21 * b05 - a23 * b03,
      a12 * b08 - a10 * b11 - a13 * b07,
      a00 * b11 - a02 * b08 + a03 * b07,
      a32 * b02 - a30 * b05 - a33 * b01,
      a20 * b05 - a22 * b02 + a23 * b01,
      a10 * b10 - a11 * b08 + a13 * b06,
      a01 * b08 - a00 * b10 - a03 * b06,
      a30 * b04 - a31 * b02 + a33 * b00,
      a21 * b02 - a20 * b04 - a23 * b00,
      a11 * b07 - a10 * b09 - a12 * b06,
      a00 * b09 - a01 * b07 + a02 * b06,
      a31 * b01 - a30 * b03 - a32 * b00,
      a20 * b03 - a21 * b01 + a22 * b00) / det;
}


vec4 try_reflect(vec4 p, vec4 n, inout int flips) {
    float k = dot(p, n);
    if (k < 0.) {
        flips += 1;
        p.xyz -= 2. * k * n.xyz;
    }
    return p;
}

vec3 do_reflect(vec3 p, vec4 n) {
    vec4 q = vec4(p, 1.);
    p -= 2. * dot(q, n) * n.xyz;
    return p;
}

vec3 rA(vec3 p) { return do_reflect(p, M[0]); }
vec3 rB(vec3 p) { return do_reflect(p, M[1]); }
vec3 rC(vec3 p) { return do_reflect(p, M[2]); }
vec3 rD(vec3 p) { return do_reflect(p, M[3]); }


// Initialize the data for Wythoff construction.
void init() {
    const float s = 0.70710678;

    if (latticeType == 0) {
        M = mat4(vec4(-s, -s, 0, 2.*s),
                 vec4(s, -s, 0, 0),
                 vec4(0, s, -s, 0),
                 vec4(0, s, s, 0));

        V = mat4x3(vec3(0, 0, 0),
                   vec3(2, 0, 0),
                   vec3(1, 1, -1),
                   vec3(1, 1, 1));
    }

    else if (latticeType == 1) {
        M = mat4(vec4(0, 0, 1, 0),
                 vec4(0, s, -s, 0),
                 vec4(s, -s, 0, 0),
                 vec4(-s, -s, 0, 2.*s));

        V = mat4x3(vec3(1, 1, 1),
                   vec3(1, 1, 0),
                   vec3(2, 0, 0),
                   vec3(0, 0, 0));
    }

    else {
        M = mat4(vec4(0, 0, 1, 0),
                 vec4(0, s, -s, 0),
                 vec4(s, -s, 0, 0),
                 vec4(-1, 0, 0, 1));

        V = mat4x3(vec3(0, 0, 0),
                   vec3(1, 0, 0),
                   vec3(1, 1, 0),
                   vec3(1, 1, 1));
    }

    M_inv = inverse(M);
    vec4 v4 = T * M_inv;
    v4 /= v4.w;
    v0 = v4.xyz;
    for (int i = 0; i < 4; i++) {
        E[i] = v0 - 2. * dot(v4, M[i]) * M[i].xyz;
    }

    if (snub) {

        spts[0] = rA(rB(v0));
        spts[1] = rB(rA(v0));
        spts[2] = rA(rC(v0));
        spts[3] = rC(rA(v0));
        spts[4] = rA(rD(v0));
        spts[5] = rD(rA(v0));
        spts[6] = rB(rC(v0));
        spts[7] = rC(rB(v0));
        spts[8] = rB(rD(v0));
        spts[9] = rD(rB(v0));
        spts[10] = rC(rD(v0));
        spts[11] = rD(rC(v0));

    }
}

bool isActive(int k) {
    return T[k] != 0.0;
}

vec2 rot2d(vec2 p, float a) { return cos(a) * p + sin(a) * vec2(p.y, -p.x); }

vec3 camPath(float t) { return vec3(t, t, t) / 2.; }

// Taken from mla's code at https://www.shadertoy.com/view/WsfcRn
vec3 fold(vec3 p, inout int flips) {
    vec4 q;

    if (latticeType == 2) {

        // fold into unit cube
        p = mod(p + 1., 2.) - 1.;
        flips += int(p.x < 0.0) + int(p.y < 0.0) + int(p.z < 0.0);
        p = abs(p);
        q = vec4(p, 1.);
        // the group generated by reflections about mirror 1, 2 is the S_3 group
        // {s, t | s^2 = t^2 = (st)^3 = 1}
        // each element can be written as a prefix of sts = tst.
        q = try_reflect(q, M[1], flips);
        q = try_reflect(q, M[2], flips);
        q = try_reflect(q, M[1], flips);
    }

    else if (latticeType == 1) {

        p = mod(p + 2., 4.) - 2.;
        flips += int(p.x < 0.0) + int(p.y < 0.0);
        p.xy = abs(p.xy);
        q = vec4(p, 1);
        q = try_reflect(q, M[0], flips);
        for (int i = 0; i < 2; i++) {
            q = try_reflect(q, M[3], flips);
            q = try_reflect(q, M[2], flips);
            q = try_reflect(q, M[1], flips);
        }
    }

    else {

        p = mod(p + 2., 4.) - 2.;
        q = vec4(p, 1);
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++)
                q = try_reflect(q, M[j], flips);
        }
    }

    return q.xyz;
}

// Shane's tex3D function
vec3 tex3D(sampler2D t, in vec3 p, in vec3 n) {
    n = max(abs(n), 0.001);
    n /= dot(n, vec3(1));
    vec3 tx = texture(t, p.yz).xyz;
    vec3 ty = texture(t, p.zx).xyz;
    vec3 tz = texture(t, p.xy).xyz;
    return (tx*tx*n.x + ty*ty*n.y + tz*tz*n.z);
}

// I hacked this function to rotate any edge (a, b) to z-axis
mat3 rotAxis(vec3 n) {
    n = normalize(n);
    vec3 x;
    if (n.x == 0.)
        x = vec3(1, 0, 0);
    else
        x = normalize(vec3(-n.y, n.x, 0.));
    vec3 y = cross(n, x);
    return mat3(x, y, n);
}


float tube(vec2 p, float sc, float rad) {
    return max(max(p.x, p.y), (p.x + p.y)*sc) - rad;
}

// draw an edge with two ends at a, b.
vec3 dSegment(vec3 p, vec3 a, vec3 b) {
    // set local origin at middle point of the edge
    vec3 m = (a + b) / 2.;
    p -= m;
    b -= m;
    a -= m;
    vec3 h = (b - a) / 2.;
    float L = length(h); // length of half the edge

    p = p * rotAxis(h);  // rotate the edge to parallel with z-axis
    p = abs(p);

    // the main tube, currently this has infinite length
    float tb;
    #ifdef use_cylinder
        tb = length(p.xy) - tbsize;
    #else
        tb = tube(p.xy, 0.75, tbsize);
    #endif
    float band = 1e5;
    float innerTb = 1e5;

    // add a band of 1/4 length of the edge
    band = max(tb - 0.0075, p.z - L/4.);

    // trick: rotate p to make two smaller tubes
    // remove them from the main tube to make the holes
    vec2 peg = vec2(tube(p.xz, .64, .0425), tube(p.yz, .64, .0425));
    float hole = min(peg.x, peg.y);

    // use planes to cut the band
    band = min(band, min(max(peg.x, p.y - tbsize - .0095), max(peg.y, p.x - tbsize - .0095)));

    // make holes on the main tube
    tb = max(tb, -(hole - .015));

    // cut the infinite main tube at the two ends
    tb = max(tb, p.z - L);

    // make holes on the band
    band = max(band, -(hole + .02));

    // use sphere to create a fake inner tube
    innerTb = length(p) - tbsize;

    return vec3(tb, band, innerTb);
}

vec3 snub0(vec3 ed, vec3 p) {
    for (int i = 0; i < spts.length(); i++) {
        ed = min(ed, dSegment(p, v0, spts[i]));
    }
    return ed;
}

vec3 snub1(vec3 ed, vec3 p) {
    for (int i = 0; i < 4; i++) {
        for (int j = i + 1; j < 4; j++)
            ed = min(ed, dSegment(p, E[i], E[j]));
    }
    return ed;
}

float map(vec3 p) {
    vec3 dedge = vec3(1e5);
    int flips = 0;
    p = fold(p, flips);

    if (snub) {
        dedge = flips %2 == 0 ? snub0(dedge, p) : snub1(dedge, p);
    }

    else {
        if (!dual) {
            for (int i = 0; i < 4; i++) {
                dedge = min(dedge, dSegment(p, v0, E[i]));
            }
        }
        else {

            if (latticeType == 2) {

                if (isActive(0) || isActive(1)) dedge = min(dedge, dSegment(p, V[2], V[3]));
                if (isActive(0) && isActive(2)) dedge = min(dedge, dSegment(p, V[1], V[3]));
                if (isActive(1) || isActive(2)) dedge = min(dedge, dSegment(p, V[0], V[3]));
                if (isActive(0) && isActive(3)) dedge = min(dedge, dSegment(p, V[1], V[2]));
                if (isActive(1) && isActive(3)) dedge = min(dedge, dSegment(p, V[0], V[2]));
                if (isActive(2) || isActive(3)) dedge = min(dedge, dSegment(p, V[0], V[1]));
            }

            else if (latticeType == 1) {

                if (isActive(0) || isActive(1)) dedge = min(dedge, dSegment(p, V[2], V[3]));
                if (isActive(0) && isActive(2)) dedge = min(dedge, dSegment(p, V[1], V[3]));
                if (isActive(1) || isActive(2)) dedge = min(dedge, dSegment(p, V[0], V[3]));
                if (isActive(0) && isActive(3)) dedge = min(dedge, dSegment(p, V[1], V[2]));
                if (isActive(1) || isActive(3)) dedge = min(dedge, dSegment(p, V[0], V[2]));
                if (isActive(2) && isActive(3)) dedge = min(dedge, dSegment(p, V[0], V[1]));
            }

            else {

                if (isActive(2) && isActive(3)) dedge = min(dedge, dSegment(p, V[0], V[1]));
                if (isActive(1) || isActive(3)) dedge = min(dedge, dSegment(p, V[0], V[2]));
                if (isActive(1) || isActive(2)) dedge = min(dedge, dSegment(p, V[0], V[3]));
                if (isActive(0) || isActive(3)) dedge = min(dedge, dSegment(p, V[1], V[2]));
                if (isActive(0) || isActive(2)) dedge = min(dedge, dSegment(p, V[1], V[3]));
                if (isActive(0) && isActive(1)) dedge = min(dedge, dSegment(p, V[2], V[3]));
            }
        }
    }

    // store the object ids.
    objIDs = dedge;

    return min(dedge.x, min(dedge.y, dedge.z));
}


vec3 calcNormal(vec3 p, inout float edge, float t) {
    vec2 e = vec2(1./mix(400., iResolution.y, .5)*(1. + t*.5), 0);

    float d1 = map(p + e.xyy), d2 = map(p - e.xyy);
    float d3 = map(p + e.yxy), d4 = map(p - e.yxy);
    float d5 = map(p + e.yyx), d6 = map(p - e.yyx);
    float d = map(p)*2.;

    edge = abs(d1 + d2 - d) + abs(d3 + d4 - d) + abs(d5 + d6 - d);
    edge = smoothstep(0., 1., sqrt(edge/e.x*2.));

    e = vec2(.002, 0);
    d1 = map(p + e.xyy), d2 = map(p - e.xyy);
    d3 = map(p + e.yxy), d4 = map(p - e.yxy);
    d5 = map(p + e.yyx), d6 = map(p - e.yyx);

    return normalize(vec3(d1 - d2, d3 - d4, d5 - d6));
}

float softShadow(vec3 ro, vec3 lp, float tmin, float tmax, float k) {
    const int maxShadeIterations = 32;
    vec3 rd = lp - ro;
    rd /= max(length(rd), 1e-4);
    float shade = 1.0;
    float t = tmin;
    for (int i = 0; i < maxShadeIterations; i++) {
        float h = map(ro + rd * t);
        t += clamp(h, 0.01, 0.2);
        shade = min(shade, smoothstep(0., 1., k * h / t));
        if (abs(h) < 1e4 || t > tmax)
            break;
    }
    return clamp(shade + 0.15, 0.0, 1.0);
}

float calcAO(vec3 p, vec3 n) {
    float occ = 0.0;
    float sca = 1.0;
    for (int i = 0; i < 5; i++) {
        float h = 0.01 + 0.15 * float(i) / 4.0;
        float d = map(p + h * n);
        occ += (h - d) * sca;
        sca *= 0.7;
    }
    return clamp(1.0 - occ, 0.0, 1.0);
}

float trace(in vec3 ro, in vec3 rd) {
    glow = 0.;
    float ah;
    const float precis = 1e-3;
    float t = 0.0;
    for (int i = 0; i < 128; i++) {
        float h = map(ro + rd * t);
        ah = abs(h);
        glow += 1./(1. + ah*ah*8.);
        if (ah < (t * 0.125 + 1.) * precis || t > FAR)
            break;
        t += h;
    }
    return min(t, FAR);
}

float n3D(vec3 p) {
    const vec3 s = vec3(7, 157, 113);
    vec3 ip = floor(p);
    p -= ip;
    vec4 h = vec4(0., s.yz, s.y + s.z) + dot(ip, s);
    p = p * p * (3. - 2. * p); //p *= p*p*(p*(p * 6. - 15.) + 10.);
    h = mix(fract(sin(h) * 43758.5453), fract(sin(h + s.x) * 43758.5453), p.x);
    h.xy = mix(h.xz, h.yw, p.y);
    return mix(h.x, h.y, p.z); // Range: [0, 1].
}

vec3 eMap(vec3 rd, vec3 sn) {
    vec3 sRd = rd;
    rd.xy -= iTime * .25;
    rd *= 3.;

    float c = n3D(rd) * .57 + n3D(rd * 2.) * .28 + n3D(rd * 4.) * .15;
    c = smoothstep(0.4, 1., c);
    vec3 col = vec3(min(c * 1.5, 1.), pow(c, 2.5), pow(c, 12.));
    return mix(col, col.yzx, sRd * .25 + .25);
}

vec3 transform(in vec3 p) {
    if (iMouse.x > 0.0) {
        float phi =   (2.0*iMouse.x - iResolution.x) / iResolution.x * PI;
        float theta = (2.0*iMouse.y - iResolution.y) / iResolution.y * PI;
        p.yz = rot2d(p.yz, theta);
        p.zx = rot2d(p.zx, -phi);
    }
    return p;
}


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    init();

    vec2 uv = (2.0 * fragCoord.xy - iResolution.xy) / iResolution.y;

    vec3 up = vec3(0, 1, 0);
    vec3 ro = camPath(iTime * 1.1);
    ro = transform(ro);
    vec3 lookat = camPath(iTime * 1.1 + 0.1);

    vec3 forward = normalize(lookat - ro);
    vec3 right = normalize(cross(forward, up));
    up = cross(right, forward);
    vec3 rd = normalize(uv.x * right + uv.y * up + forward * 2.);
    rd = transform(rd);
    vec3 lp = camPath(iTime * 1.1 + 1.);
    vec3 loffs = vec3(0, 1, 0);
    vec2 a = sin(vec2(1.57, 0) - lp.z * 1.57 / 10.);
    loffs.xy = mat2(a, -a.y, a.x) * loffs.xy;
    lp += loffs;
    lp = transform(lp);
    vec3 col = vec3(0);

    float t = trace(ro, rd);

    float objID = (objIDs.x < objIDs.y && objIDs.x < objIDs.z) ? 0. : (objIDs.y < objIDs.z) ? 1. : 2.;

    if (t < FAR) {
        float ed;
        vec3 pos = ro + t * rd;
        vec3 nor = calcNormal(pos, ed, t);

        vec3 oCol;
        #ifndef GOLD_STYLE
        vec3 bCol = mix(vec3(1, .1, .5).zyx,
                        vec3(1, .3, .1).zyx,
                        dot(sin(pos*8. - cos(pos.yzx*4. + iTime*4.)), vec3(.166)) + .5);
        #else
        vec3 bCol = mix(vec3(1, .5, .1),
                        vec3(1, .1, .2),
                        dot(sin(pos*8. - cos(pos.yzx*4. + iTime*4.)), vec3(.166)) + .5);
        #endif
        if(objID < .5)
            oCol = mix(bCol, vec3(1), .97);

        else if (objID > 1.5)
            oCol = mix(bCol, vec3(1), .05) + bCol*2.;

        else
            oCol = mix(bCol, vec3(1.35), .97)*vec3(1.1, 1, .9);

        vec3 tx = tex3D(iChannel0, pos*2., nor);
        tx = smoothstep(.0, .5, tx)*2.;

        if(objID < 1.5)
            oCol *= tx;
        else
            oCol *= mix(vec3(1), tx, .5);

        float ao = calcAO(pos, nor);
        float sh = softShadow(pos + nor*.002, lp, 0.08, 16., t);

        vec3 ld = lp - pos;
        float dist = max(length(ld), 0.001);
        ld /= dist;

        float atten = 1./(1. + dist*0.1 + dist*dist*0.05);

        float diff = max(dot(ld, nor), 0.);
        if (objID < 1.5)
            diff = pow(diff, 4.)*2.;
        float spec = pow(max(dot( reflect(ld, nor), rd), 0.0 ), 32.0);

        col = oCol*(diff + ao*.2) + mix(bCol.zyx, vec3(1, .7, .3), .5)*spec*4.;

        col += .015/max(abs(.05 - map(pos*1.5 + sin(iTime/6.))), .01)*oCol*mix(bCol, vec3(1, .8, .5), .35);

        // Adding a bit of glow. It was tempting to get my money's worth, but I kept it subtle. :)
        if(objID < 1.5)
            col += bCol*glow*.025;
        else
            col += bCol*glow*1.5;

        // Applying the dark edges, attenuation, shadows and ambient occlusion.
        col *= (1. - ed*.7);
        col *= atten*(sh + ao*.25)*ao;

    }

    float fog = 1./(1. + t*.125 + t*t*.01);
    col = mix(vec3(0), col, fog);

    uv = fragCoord/iResolution.xy;
    col *= pow(16.*uv.x*uv.y*(1. - uv.x)*(1. - uv.y) , .125);
    fragColor = vec4(sqrt(max(col, 0.)), 1);
}
