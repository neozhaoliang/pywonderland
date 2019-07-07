#version 130

struct Mobius { vec2 A, B, C, D; };

uniform vec3          iResolution;
uniform float         iTime;
uniform bool          iApply;
uniform bool          iHyperbolic;
uniform bool          iElliptic;
uniform Mobius        iMobius;
uniform int           AA;


out vec4 FinalColor;


#define PI 3.14159265358979
#define e_  2.71828182845904

// Raymarching constants
#define MIN_TRACE_DIST   0.01
#define MAX_TRACE_DIST   100.0
#define MAX_TRACE_STEPS  128
#define PRECISION        1e-4

// Time constants
#define SPEED            (iTime * 2.5)
#define hue_speed        (iTime * 1.8)

// Scene constants
const vec2 polar_grid = vec2(0.4, PI / 7.0);
const vec2 cone_angle = normalize(vec2(1.5, 1.0));
const float horo_sphere_radius = 0.9;

// Intensity constants
const float intensity_divisor = 4.0 * 1e4;
const float intensity_factor_max = 7.2;
const float center_intensity = 12.0;
const float dist_factor = 3.0;
const float ppow = 1.9;

// Color constants
const float center_hue = 0.5;
const float center_sat = 0.18;

// Shape constants
const float strong_factor = 0.25;
const float weak_factor = 0.19;
const vec2 star_hv_factor = vec2(9.0, 0.3);
const vec2 star_diag_factor = vec2(12.0, 0.6);

bool parabolic;


// complex operations
vec2  C_Conj(vec2 z)         { return vec2(z.x, -z.y); }
vec2  C_Mult(vec2 z, vec2 w) { return vec2(z.x * w.x - z.y * w.y, z.x * w.y + z.y * w.x); }
vec2  C_Div(vec2 z, vec2 w)  { return C_Mult(z, C_Conj(w)) / dot(w, w); }
vec2  C_Inv(vec2 z)          { return C_Conj(z) / dot(z, z); }
vec2  C_Sqrt(vec2 z)
{
    float r2 = dot(z, z);
    float r = sqrt(sqrt(r2));
    float angle = atan(z.y, z.x);
    return r * vec2(cos(angle / 2.0), sin(angle / 2.0));
}

// quaternion operations
vec4 Q_Mult(vec4 p, vec4 q) { return vec4(p.x * q.x - dot(p.yzw, q.yzw), p.x * q.yzw + q.x * p.yzw + cross(p.yzw, q.yzw));}
vec4 Q_Div(vec4 p, vec4 q)  { return Q_Mult(p, vec4(q.x, -q.yzw) / dot(q, q)); }

// Mobius transformation opertations
vec2 M_Apply(Mobius m, vec2 z) { return C_Div(C_Mult(m.A, z) + m.B, C_Mult(m.C, z) + m.D); }
vec4 M_Apply(Mobius m, vec4 q) {
    vec4 a = vec4(m.A, 0.0, 0.0);
    vec4 b = vec4(m.B, 0.0, 0.0);
    vec4 c = vec4(m.C, 0.0, 0.0);
    vec4 d = vec4(m.D, 0.0, 0.0);
    return Q_Div(Q_Mult(a, q) + b, Q_Mult(c, q) + d);
}

// convertion between Euclidean distance and hyperbolic distance in the upper space
float e2h(float d) { return log(d); }
float h2e(float d) { return pow(e_, d); }

// 1d and 2d rectangular/sperical grid
float grid1d(float x, float size)  { return mod(x + 0.5 * size, size) - 0.5 * size; }
vec2  grid2d(vec2 p, vec2 size)    { return mod(p + 0.5 * size, size) - 0.5 * size; }
vec2  polarGrid(vec2 p, vec2 size) {
    float theta = atan(p.y, p.x), r = e2h(length(p));
    return grid2d(vec2(r, theta), size);
}

// view to world transformation
mat3 viewMatrix(vec3 camera, vec3 lookat, vec3 up) {
    vec3 f = normalize(lookat - camera);
    vec3 r = normalize(cross(f, up));
    vec3 u = normalize(cross(r, f));
    return mat3(r, u, -f);
}

// signed distance functions for plane y=0 and y=c
float sdPlane(vec3 p)          { return p.y; }
float sdPlane(vec3 p, float c) { return p.y - c; }
// signed distance function for sphere kissing at y=0 with radius r
float sdSphere(vec3 p, float r) {
    p.y -= r;
    return length(p) - r;
}

// hsv to rgb conversion
vec3 hsv2rgb(vec3 hsv)
{
    const vec3 p = vec3(0.0, 2.0/3.0, 1.0/3.0);
    hsv.yz = clamp(hsv.yz, 0.0, 1.0);
    return hsv.z * (0.63 * hsv.y * (cos(2 * PI *(hsv.x + p)) - 1.0) + 1.0);
}

// 2d rotation
vec2 R(vec2 p, float a) { return cos(a) * p + sin(a) * vec2(p.y, -p.x); }

/*-------------------------
    Mobius transformations
  -------------------------*/

// A Mobius transformation of hyperbolic type is conjugate to a pure scaling
void isometryHyperbolic(inout vec2 p) {
    float d = grid1d(e2h(length(p)) - SPEED * polar_grid.x, polar_grid.x);
    p = normalize(p) * h2e(d);
}

// A Mobius transformation of elliptic type is conjugate to a pure rotation
void isometryElliptic(inout vec2 p) { p = R(p, SPEED * polar_grid.y); }

// A Mobius transformation of parabolic type is conjugate to a pure translation
void isometryParabolic(inout vec2 p) { p.x += iTime * polar_grid.x / 3.0; }

float applyMobius(inout vec3 p) {
    if (!iApply) return 1.0;
    p = M_Apply(iMobius, vec4(p, 0)).xyz;
    float scale = length(p);
    return scale > 1.0 ? 1.0 / scale : scale;
}

// a cone in the upper hyperbolic space may be a usual cone
// at the origin or a Dupin cyclide with its two horns on the plane
float sdCone(vec3 p)
{
    float t = 1.0;
    if (iApply) {
        t = applyMobius(p);
        p = normalize(p);
    }
    float q = length(p.xz);
    return dot(cone_angle, vec2(q, -p.y)) * t;
}

// signed distance function for parabolic case
float sdScene1(vec3 p) { return iApply ? min(sdPlane(p), sdSphere(p, horo_sphere_radius)) : sdPlane(p, 0.5 / horo_sphere_radius); }

// signed distance function for elliptic/hyperbolic case
float sdScene2(vec3 p) { return min(sdPlane(p), sdCone(p)); }

float getIntensity1(vec2 p) {
    // Horizontal and vertical branches
    float dist  = length(p);
    float disth = length(p * star_hv_factor);
    float distv = length(p * star_hv_factor.yx);

    // Diagonal branches
    vec2 q = 0.7071 * vec2(dot(p, vec2(1.0, 1.0)), dot(p, vec2(1.0, -1.0)));
    float dist1 = length(q * star_diag_factor);
    float dist2 = length(q * star_diag_factor.yx);

    // Middle point star intensity
    float pint1 = 1.0 / (dist * dist_factor + 0.015)
                + strong_factor / (disth * dist_factor + 0.01)
                + strong_factor / (distv * dist_factor + 0.01)
                + weak_factor / (dist1 * dist_factor + 0.01)
                + weak_factor / (dist2 * dist_factor + 0.01);

    if(pint1 * intensity_factor_max > 6.0)
        return center_intensity * intensity_factor_max * pow(pint1, ppow) / intensity_divisor;
    return 0.0;
}

float getIntensity2(vec2 p) {
    float angle = atan(polar_grid.x, polar_grid.y);
    float dist  = length(p);
    float disth = length(p * star_hv_factor);
    float distv = length(p * star_hv_factor.yx);

    vec2 q1 = R(p, angle);
    float dist1 = length(q1 * star_diag_factor);
    vec2 q2 = R(p, -angle);
    float dist2 = length(q2 * star_diag_factor);

    float pint1 = 1.0 / (dist * dist_factor + 0.015)
                + strong_factor / (disth * dist_factor + 0.01)
                + strong_factor / (distv * dist_factor + 0.01)
                + weak_factor / (dist1 * dist_factor + 0.01)
                + weak_factor / (dist2 * dist_factor + 0.01);
    if(pint1 * intensity_factor_max > 6.0)
        return intensity_factor_max * pow(pint1, ppow) / intensity_divisor * center_intensity * 3.0;
    return 0.0;
}

vec3 getColor(vec2 p, float pint) {
    float sat = 0.75 / pow(pint, 2.5) + center_sat;
    float time2 = parabolic ?
                  hue_speed - length(p.y) / 5.0 :
                  hue_speed - e2h(length(p)) / 7.0;
    float hue = center_hue + time2;
    return hsv2rgb(vec3(hue, sat, pint)) + pint / 3.0;
}

float trace(vec3 ro, vec3 rd, out vec2 p, out float pint) {
    float depth = MIN_TRACE_DIST;
    float dist;
    vec3 pos;
    for (int i = 0; i < MAX_TRACE_STEPS; i++) {
        pos = ro + rd * depth;
        dist = parabolic ? sdScene1(pos) : sdScene2(pos);
        if (dist < PRECISION || depth >= MAX_TRACE_DIST) break;
        depth += dist;
    }
    if (parabolic) {
        if (iApply) pos /= dot(pos, pos);
        p = pos.xz;
        isometryParabolic(pos.xz);
        pos.xz = grid2d(pos.xz, vec2(polar_grid.x / 2.0));
        pint = getIntensity1(pos.xz);
    }
    else {
        applyMobius(pos);
        p = pos.xz;
        if (iHyperbolic) isometryHyperbolic(pos.xz);
        if (iElliptic)   isometryElliptic(pos.xz);
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

void main() {
    parabolic = !(iElliptic || iHyperbolic);

    vec3 ro = vec3(-2.0, 4.0, 6.0);
    vec3 lookat = vec3(0.0, 0.6, 0.0);
    vec3 up = vec3(0.0, 1.0, 0.0);
    mat3 M = viewMatrix(ro, lookat, up);
    vec3 tot = vec3(0.1);
    for (int ii = 0; ii < AA; ii++) {
        for (int jj = 0; jj < AA; jj++) {
            vec2 offset = vec2(float(ii), float(jj)) / float(AA);
            vec2 uv = (gl_FragCoord.xy + offset) / iResolution.xy;
            uv = 2.0 * uv - 1.0;
            uv.x *= iResolution.x / iResolution.y;
            vec3 rd = M * normalize(vec3(uv, -4.0));
            vec2 p;
            float pint;
            float dist = trace(ro, rd, p, pint);
            if (dist >= 0.0)
                tot += tonemap(4.0 * getColor(p, pint));
        }
    }
    tot /= float(AA * AA);
    FinalColor = vec4(tot, 1.0);
}
