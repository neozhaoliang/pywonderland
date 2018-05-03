#version 120

/*
    Complex operations
*/

vec2 C_Conj(vec2 z)
{
    return vec2(z.x, -z.y);
}

vec2 C_Mult(vec2 z, vec2 w)
{
    return vec2(z.x * w.x - z.y * w.y, z.x * w.y + z.y * w.x);
}

float C_MagSquared(vec2 z)
{
    return z.x * z.x + z.y * z.y;
}

vec2 C_Div(vec2 z, vec2 w)
{
    return C_Mult(z, C_Conj(w)) / C_MagSquared(w);
}

vec2 C_Inv(vec2 z)
{
    return C_Conj(z) / C_MagSquared(z);
}

vec2 C_Sqrt(vec2 z)
{
    float r2 = C_MagSquared(z);
    float r = sqrt(sqrt(r2));
    float angle = atan(z.y, z.x);
    return r * vec2(cos(angle / 2.0), sin(angle / 2.0));
}


/*
    Quaternion operations
*/

float Q_MagSquared(vec4 q)
{
    return dot(q, q);
}

vec4 Q_Mult(vec4 p, vec4 q)
{
    return vec4(p.x * q.x - dot(p.yzw, q.yzw),
                p.x * q.yzw + q.x * p.yzw + cross(p.yzw, q.yzw));
}

vec4 Q_Div(vec4 p, vec4 q)
{
    float mag = Q_MagSquared(q);
    vec4 q_inv = vec4(q.x, -q.yzw) / mag;
    return Q_Mult(p, q_inv);
}


/*
    Mobius transformations
*/

struct Mobius
{
    vec2 A;
    vec2 B;
    vec2 C;
    vec2 D;
};

Mobius M_Scale(Mobius m, vec2 s)
{
    Mobius result;
    result.A = C_Mult(m.A, s);
    result.B = C_Mult(m.B, s);
    result.C = C_Mult(m.C, s);
    result.D = C_Mult(m.D, s);
    return result;
}

Mobius M_Normalize(Mobius m)
{
    vec2 k = C_Inv(C_Sqrt(m.A * m.D - m.B * m.C));
    return M_Scale(m, k);
}

Mobius M_Mult(Mobius a, Mobius b)
{
    Mobius result;
    result.A = C_Mult(a.A, b.A) + C_Mult(a.B, b.C);
    result.B = C_Mult(a.A, b.B) + C_Mult(a.B, b.D);
    result.C = C_Mult(a.C, b.A) + C_Mult(a.D, b.C);
    result.D = C_Mult(a.C, b.B) + C_Mult(a.D, b.D);
    return M_Normalize(result);
}

vec2 M_Apply(Mobius m, vec2 z)
{
    return C_Div(C_Mult(m.A, z) + m.B, C_Mult(m.C, z) + m.D);
}

vec4 M_Apply(Mobius m, vec4 q)
{
    vec4 a = vec4(m.A, 0.0, 0.0);
    vec4 b = vec4(m.B, 0.0, 0.0);
    vec4 c = vec4(m.C, 0.0, 0.0);
    vec4 d = vec4(m.D, 0.0, 0.0);
    return Q_Div(Q_Mult(a, q) + b, Q_Mult(c, q) + d);
}


/*
    Convert between Euclidean distance and
    hyperbolic distance in upper halfspace
*/

# define e_ 2.71828182846

float UHStoH(float e)
{
    return log(e);
}

float HtoUHS(float h)
{
    return pow(e_, h);
}


/*
    Rotation in the 2D plane
*/

vec2 Rotate2d(vec2 p, float t)
{
    return vec2(p.x * cos(t) - p.y * sin(t),
                p.y * cos(t) + p.x * sin(t));
}


/*
    1d and 2d grid
*/

void Mod(inout float x, float size)
{
    x = mod(x + 0.5 * size, size) - 0.5 * size;
}

void Mod2d(inout vec2 p, vec2 size)
{
    p = mod(p + 0.5 * size, size) - 0.5 * size;
}


/*
    Spherical grid in two dimensions
*/

void Mod2dPolar(inout vec2 p, vec2 size)
{
    float phase = atan(p.y, p.x);
    float modulus = UHStoH(length(p));
    Mod(phase, size.y);
    Mod(modulus, size.x);
    p = vec2(modulus, phase);
}


#define PI 3.141592653
#define TWOPI (2 * PI)

/*
  Convert hsv color to rgb color
*/

vec3 hsv2rgb(vec3 hsv)
{
    const vec3 p = vec3(0.0, 2.0/3.0, 1.0/3.0);
    hsv.yz = clamp(hsv.yz, 0.0, 1.0);
    return hsv.z * (0.63 * hsv.y * (cos(TWOPI *(hsv.x + p)) - 1.0) + 1.0);
}


/*
  Transform objects in view space to model space
*/

mat3 viewMatrix(vec3 eye, vec3 lookat, vec3 up)
{
    vec3 f = normalize(lookat - eye);
    vec3 r = normalize(cross(f, up));
    vec3 u = normalize(cross(r, f));
    return mat3(r, u, -f);
}


/*
    Get ray directions
*/

vec3 rayDirection(float fov, vec2 size, vec2 fragCoord) {
    vec2 xy = fragCoord - size / 2.0;
    float z = size.y / tan(radians(fov) / 2.0);
    return normalize(vec3(xy, -z));
}


/*
    Constructive solid geometry union operation on SDF-calculated distances.
*/

float unionSDF(float distA, float distB) {
    return min(distA, distB);
}


/*
  Signed distance function for a sphere kissing the origin with radius r.
*/

float sphereSdf(vec3 p, float r)
{
    p.z -= r;
    return length(p) - r;
}


/*
  Signed distance functions for the z=0 and z=c planes
*/

float planeSdf(vec3 p)
{
    return length(p.z);
}

float planeSdf(vec3 p, float planeOffset)
{
    return length(p.z) - planeOffset;
}
