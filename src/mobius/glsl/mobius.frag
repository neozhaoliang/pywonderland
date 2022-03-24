uniform bool u_apply;
uniform bool u_elliptic;
uniform bool u_hyperbolic;
uniform bool u_riemann;
uniform int  AA;

#define PI  3.1415926536
#define E_  2.7182818285

// Raymarching constants
#define MIN_TRACE_DIST   0.01
#define MAX_TRACE_STEPS  255
#define PRECISION        1e-5
#define FAR              100.

// Animation speed
#define anim_speed (iTime * .5)
#define hue_speed  (iTime * .3)

// grid and cone size
const vec2 polar_grid = vec2(0.4, PI / 7.0);
const vec2 cone_angle = normalize(vec2(1.5, 1.0));

// Intensity constants
const float intensity_divisor = 40000.;
const float intensity_factor_max = 7.2;
const float center_intensity = 12.;
const float dist_factor = 3.;
const float ppow = 1.9;

// Color constants
const float center_hue = 0.5;
const float center_sat = 0.18;

// shape constants
const float strong_factor = 7.;
const float weak_factor = 1.;
const vec2 star_hv_factor = vec2(30, 1);
const vec2 star_diag_factor = vec2(30, 1);
//const vec2 star_hv_factor = vec2(9.0, 0.3);
//const vec2 star_diag_factor = vec2(12.0, 0.6);

// b_parabolic is true if u_elliptic and b_parabolic are both false
// b_loxodromic is true if u_elliptic and b_parabolic are both true
bool b_parabolic, b_loxodromic;

// hsv to rgb conversion
vec3 hsv2rgb(vec3 hsv) {
    const vec3 p = vec3(0.0, 2.0/3.0, 1.0/3.0);
    hsv.yz = clamp(hsv.yz, 0.0, 1.0);
    return hsv.z*(0.63*hsv.y*(cos(2.*PI*(hsv.x + p)) - 1.0) + 1.0);
}

// Conversion between Euclidean distance and hyperbolic distance
// in upper half space. They are inverse of each other.
float eucToHyp(float d) { return log(d); }
float hypToEuc(float d) { return pow(E_, d); }

// 2d rotation
vec2 rot2d(vec2 p, float a) { return cos(a) * p + sin(a) * vec2(p.y, -p.x); }

// 1d and 2d rectangular grids
float grid1d(float x, float size) {
    return mod(x + 0.5 * size, size) - 0.5 * size;
}

vec2 grid2d(vec2 p, vec2 size) {
    return mod(p + 0.5 * size, size) - 0.5 * size;
}

// 2d polar grids
vec2 polarGrid(vec2 p, vec2 size) {
    float theta = atan(p.y, p.x);
    float r = eucToHyp(length(p));
    return grid2d(vec2(r, theta), size);
}

/*
 * Complex arithmetic
*/
vec2 cmul(vec2 z, vec2 w) {
    return vec2(z.x * w.x - z.y * w.y, z.x * w.y + z.y * w.x);
}

vec2 cdiv(vec2 z, vec2 w) {
    return vec2(z.x * w.x + z.y * w.y, -z.x * w.y + z.y * w.x) / dot(w, w);
}

vec2 csqrt(vec2 z) {
    float r2 = dot(z, z);
    float r = sqrt(sqrt(r2));
    float angle = atan(z.y, z.x);
    return r * vec2(cos(angle / 2.0), sin(angle / 2.0));
}

/*
 * Quaternion arithmetic
*/
vec4 qmul(vec4 p, vec4 q) {
    return vec4(p.x * q.x - dot(p.yzw, q.yzw),
                p.x * q.yzw + q.x * p.yzw + cross(p.yzw, q.yzw));
}

vec4 qdiv(vec4 p, vec4 q) {
    return qmul(p, vec4(q.x, -q.yzw) / dot(q, q));
}

/*
 * Mobius transformation z --> (Az + B) / (Cz + D)
*/
struct Mobius {
    vec2 A, B, C, D;
};

const Mobius mob = Mobius(
    vec2(-1, 0),
    vec2(1.2, 0),
    vec2(-1, 0),
    vec2(-1.2, 0)
);

// Apply Mobius transformation on complex plane
vec2 applyMobius(vec2 z) {
    vec2 z1 = cmul(mob.A, z) + mob.B;
    vec2 z2 = cmul(mob.C, z) + mob.D;
    return cdiv(z1, z2);
}

// Apply Mobius transformation on upper half space as quaternions
// (x, y, z) --> (x + yi + zj + 0k)
vec4 applyMobius(vec4 p) {
    vec4 p1 = qmul(vec4(mob.A, 0., 0.), p) + vec4(mob.B, 0., 0.);
    vec4 p2 = qmul(vec4(mob.C, 0., 0.), p) + vec4(mob.D, 0., 0.);
    return qdiv(p1, p2);
}

float applyMobius(inout vec3 p) {
    if (!u_apply)
        return 1.0;

    p = applyMobius(vec4(p, 0)).xyz;
    float scale = length(p);
    return scale > 1.0 ? 1.0 / scale : scale;
}

// A Mobius transformation of hyperbolic type is conjugate to a pure scaling
void trans_hyperbolic(inout vec2 p) {
    float d = eucToHyp(length(p)) - anim_speed * polar_grid.x;
    // This avoids running out of resolution.
    d = grid1d(d, polar_grid.x);
    p = normalize(p) * hypToEuc(d);
}

// A Mobius transformation of elliptic type is conjugate to a pure rotation
void trans_elliptic(inout vec2 p) {
    p = rot2d(p, anim_speed * polar_grid.y);
}

// A Mobius transformation of parabolic type is conjugate to a pure translation
void trans_parabolic(inout vec2 p) {
    p.x += iTime * polar_grid.x / 3.;
}

// signed distance function for sphere kissing at y=0 with radius r
float sdSphere(vec3 p, float r) { p.y -= r; return length(p) - r; }
// signed distance functions for plane y=0 and y=c
float sdPlane(vec3 p) { return p.y; }
float sdPlane(vec3 p, float c) { return p.y - c; }
// a cone in the upper hyperbolic space may be a usual cone at the origin
// or a Dupin cyclide with its two horns on the plane
float sdCone(vec3 p) {
    float t = 1.0;
    if (u_apply) {
        t = applyMobius(p);
        p = normalize(p);
    }
    float q = length(p.xz);
    return dot(cone_angle, vec2(q, -p.y)) * t;
}

// signed distance function for parabolic case
float sdScene1(vec3 p) {
    return u_apply ? min(sdPlane(p), sdSphere(p, 1.0)) : sdPlane(p, 0.5);
}

// signed distance function for elliptic/hyperbolic case
float sdScene2(vec3 p) {
    if (u_riemann)
        return min(sdPlane(p), sdSphere(p, 1.));

    return min(sdPlane(p), sdCone(p));
}

vec3 getColor(vec2 p, float pint) {
    float sat = 0.75 / pow(pint, 2.5) + center_sat;
    // change hue by time
    float hue2 = b_parabolic ?
    hue_speed - length(p.y) / 5.0 :
    hue_speed - eucToHyp(length(p)) / 7.0;
    float hue = center_hue + hue2;
    return hsv2rgb(vec3(hue, sat, pint)) + pint / 3.;
}

float getIntensity1(vec2 p) {
    float dist = length(p);
    float disth = length(p * star_hv_factor);
    float distv = length(p * star_hv_factor.yx);

    vec2 q = 0.7071 * vec2(dot(p, vec2(1.)), dot(p, vec2(1., -1.)));
    float dist1 = length(q * star_diag_factor);
    float dist2 = length(q * star_diag_factor.yx);

    // Middle point star intensity
    float pint1 = .5 / (dist * dist_factor + 0.015)
        + strong_factor / (distv * dist_factor + 0.01)
        + weak_factor / (disth * dist_factor + 0.01)
        + weak_factor / (dist1 * dist_factor + 0.01)
        + weak_factor / (dist2 * dist_factor + 0.01);

    return center_intensity * intensity_factor_max * pow(pint1, ppow) / intensity_divisor / 2.;
}

float getIntensity2(vec2 p) {
    float angle = atan(polar_grid.x, polar_grid.y);
    float dist  = length(p);
    float disth = length(p * star_hv_factor);
    float distv = length(p * star_hv_factor.yx);

    vec2 q1 = rot2d(p, angle);
    float dist1 = length(q1 * star_diag_factor);
    vec2 q2 = rot2d(p, -angle);
    float dist2 = length(q2 * star_diag_factor);

    float pint1 = 1. / (dist * dist_factor  + .5);
    if (b_loxodromic) {
        pint1 = strong_factor / (dist2 * dist_factor + 0.01)
            + weak_factor  / (dist1 * dist_factor + 0.01)
            + weak_factor / (disth * dist_factor + 0.01)
            + weak_factor / (distv * dist_factor + 0.01);
    }
    else if (u_elliptic) {
        pint1 += weak_factor / (distv * dist_factor + 0.01) +
            strong_factor / (disth * dist_factor + 0.01) +
            weak_factor / (dist1 * dist_factor + 0.01) +
            weak_factor / (dist2 * dist_factor + 0.01);
    }
    else {
        pint1 += weak_factor / (disth * dist_factor + 1.) +
            strong_factor / (distv * dist_factor + .01) +
            weak_factor / (dist1 * dist_factor + 0.01) +
            weak_factor / (dist2 * dist_factor + 0.01);
    }
    return intensity_factor_max * pow(pint1, ppow) / intensity_divisor * center_intensity * 3.;
}

float map(vec3 pos) {
    return b_parabolic ? sdScene1(pos) : sdScene2(pos);
}

vec3 getNormal(vec3 p) {
    vec2 e = vec2(.003, 0);
    float d1 = map(p + e.xyy), d2 = map(p - e.xyy);
    float d3 = map(p + e.yxy), d4 = map(p - e.yxy);
    float d5 = map(p + e.yyx), d6 = map(p - e.yyx);
    float d = map(p) * 2.;
    return normalize(vec3(d1 - d2, d3 - d4, d5 - d6));
}

float softShadow(vec3 ro, vec3 ld, float tmin, float tmax, float k) {
    const int maxShadeIterations = 20;
    float res = 1.0;
    float t = tmin;
    for (int i = 0; i < maxShadeIterations; i++) {
        float h = map(ro + ld * t);
        res = min(res, smoothstep(0., 1., k * h / t));
        t += clamp(h, 0.01, 0.2);
        if (h < 0. || t > tmax)
            break;
    }
    return clamp(res + 0.2, 0.0, 1.0);
}


// iq's ambient occlusion
float calcAO(vec3 p, vec3 n) {
    float occ = 0.0;
    float sca = 1.0;
    for (int i = 0; i < 5; i++) {
        float h = 0.01 + 0.15 * float(i) / 4.0;
        float d = map(p + h * n);
        occ += (h - d) * sca;
        sca *= 0.7;
    }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}

float trace(vec3 ro, vec3 rd, out vec2 p, out float pint) {
    float depth = MIN_TRACE_DIST;
    float dist;
    vec3 pos;
    for (int i = 0; i < MAX_TRACE_STEPS; i++) {
        pos = ro + rd * depth;
        dist = b_parabolic ? sdScene1(pos) : sdScene2(pos);
        if (dist < PRECISION || depth >= FAR)
            break;
        depth += dist;
    }
    if (b_parabolic) {
        if (u_apply)
            pos /= dot(pos, pos);

        p = pos.xz;
        trans_parabolic(pos.xz);
        pos.xz = grid2d(pos.xz, vec2(polar_grid.x / 2.0));
        pint = getIntensity1(pos.xz);
    }
    else {
        applyMobius(pos);
        p = pos.xz;
        if (u_hyperbolic) trans_hyperbolic(pos.xz);
        if (u_elliptic)   trans_elliptic(pos.xz);
        pos.xz = polarGrid(pos.xz, polar_grid);
        pint = getIntensity2(pos.xz);
    }
    return depth;
}

// ACES tone mapping
// https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/
vec3 tonemap(vec3 color) {
    const float A = 2.51;
    const float B = 0.03;
    const float C = 2.43;
    const float D = 0.59;
    const float E = 0.14;
    return (color * (A * color + B)) / (color * (C * color + D) + E);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord) {
    b_parabolic = !(u_elliptic || u_hyperbolic);
    b_loxodromic = u_elliptic && u_hyperbolic;
    vec3 ro = vec3(-3.0, 4.8, 7.0);
    ro.xz = rot2d(ro.xz, iTime*0.3);
    vec3 lookat = vec3(0.0, 0.6, 0.0);
    vec3 up = vec3(0.0, 1.0, 0.0);
    vec3 f = normalize(lookat - ro);
    vec3 r = normalize(cross(f, up));
    vec3 u = normalize(cross(r, f));

    vec3 lp = ro + vec3(.2, .8, -0.2);

    vec3 tot = vec3(0);

    for (int ii = 0; ii < AA; ii++) {
        for (int jj = 0; jj < AA; jj++) {
            vec2 offset = vec2(float(ii), float(jj)) / float(AA);
            vec2 uv = (fragCoord + offset) / iResolution.xy;
            uv = 2.0 * uv - 1.0;
            uv.x *= iResolution.x / iResolution.y;
            vec3 rd = normalize(uv.x * r + uv.y * u + 4.0 * f);
            vec2 p;
            float pint;
            float t = trace(ro, rd, p, pint);
            if (t >= 0.0) {
                vec3 col = tonemap(4.0 * getColor(p, pint));
                vec3 pos = ro + rd * t;
                vec3 nor = getNormal(pos);
                vec3 ld = lp - pos;
                float dist = max(length(ld), 0.001);
                ld /= dist;
                float at = 2.2 / (1. + dist*.1 + dist*dist*.05);
                float ao = calcAO(pos, nor);
                float sh = softShadow(pos, ld, 0.04, dist, 8.);

                float diff = clamp(dot(nor, ld), 0.0, 1.0);
                float spec = max( 0.0, dot( reflect(-ld, nor), -rd));
                spec = pow(spec, 50.0);
                tot += diff * 2.5 * col + vec3(0.6, 0.8, 0.8) * spec * 2.;
                tot *= ao * sh * at;
            }
            if(t >= FAR)
                lp = normalize(lp - ro - rd*FAR);

            vec3 bg = mix(vec3(.5, .7, 1), vec3(1, .5, .6), .5 - .5*lp.y) * 1.3;
            tot = mix(clamp(tot, 0., 1.), bg, smoothstep(0., FAR-2., t));
        }
    }
    tot /= float(AA * AA);
    fragColor = vec4(sqrt(clamp(tot, 0., 1.)), 1.0);
}
