#version 130

uniform vec3    iResolution;
uniform float   iTime;
uniform vec4    iMouse;
uniform int     AA;
uniform vec3    PQR;
uniform vec4    truncType;

out vec4 FinalColor;

#define FOV_DIST         2.0
#define ITERATIONS       20
#define MAX_TRACE_STEPS  150
#define MAX_TRACE_DIST   2.0
#define MIN_TRACE_DIST   1e-4
#define PRECISION        1e-4
#define PI               3.141592653589793


const vec3 vertexColor = vec3(1.0, 1.0, 0.0);
const mat4x3 segmentColors = mat4x3(
    vec3(1.0, 0.0, 0.0),
    vec3(0.0, 1.0, 1.0),
    vec3(0.5, 0.7, 0.35),
    vec3(0.7, 0.2, 0.9)
);

const float VRadius = 0.028;
const float SRadius = 0.013;
const float CSphRad = 0.9998;

mat4 M;  // normal vectors of the mirrors
vec4 v0;  // initial vertex for Wythoff's construction
float cVR, sVR, cSR, sSR;

/*------------------------------------
  Math stuff about hyperbolic geoemtry
--------------------------------------*/

float hDot(vec4 p, vec4 q)
{
    return dot(p.xyz, q.xyz) - p.w * q.w;
}

float hLength(vec4 p)
{
    return sqrt(-hDot(p, p));
}

vec4 hNormalize(vec4 p)
{
    return p / hLength(p);
}

vec4 stereoInverse(vec3 p)
{
    return vec4(2 * p, (1 + dot(p, p))) / (1 - dot(p, p));
}

// reflect p about a plane with normal n if they are in different half spaces
vec4 hReflect(vec4 p, vec4 n)
{
    return p - 2.0 * min(hDot(p, n), 0.0) * n;
}

float hDist2eDist(float ca, float sa, float r)
{
    return (2.0 * r * ca + (1.0 + r*r) * sa) / ((1.0 + r*r) * ca + 2.0 * r * sa + 1.0 - r*r) - r;
}

// precompute M and v0
void init()
{
    float p = PQR.x, q = PQR.y, r = PQR.z;
    float cp = cos(PI / p), sp = sin(PI / p);
    float cq = cos(PI / q), sq = sin(PI / q);
    float cr = cos(PI / r), sr = sin(PI / r);
    // the fundamental domain lies in the all-positive orthant and the normal
    // vectors of the mirrors all point into the fundamental domain
    // note these normal vectors are normalized in the hyperbolic sense
    vec4 na = vec4(1.0, 0.0, 0.0, 0.0);
    vec4 nb = vec4(0.0, 1.0, 0.0, 0.0);
    vec4 nc = vec4(0.0, -cr, sr, 0.0);
    vec4 nd = vec4(-cp, -cq, -cq*cr/sr, 0.0);
    nd.w = -sqrt(dot(nd.xyz, nd.xyz) - 1.0);
    M = mat4(na, nb, nc, nd);

    // pabc is orthogonal to {na, nb, nc}, pbcd is orthogonal to {nb, nc, nd}, ... etc.
    // note they all have non-negative entries.
    vec4 pabc = vec4(0.0, 0.0, 0.0, 1.0);
    vec4 pbcd = vec4(-nd.w, 0.0, 0.0, cp);
    vec4 pcda = vec4(0.0, -sr*nd.w, -cr*nd.w, cr*cr*cq/sr+cq*sr);
    vec4 pdab = vec4(0.0, 0.0, -nd.w, -nd.z);
    v0 = hNormalize(mat4(pabc, pbcd, pcda, pdab) * truncType);

    cVR = cosh(VRadius);
    sVR = sinh(VRadius);
    cSR = cosh(SRadius);
    sSR = sinh(SRadius);
}

vec4 fold(vec4 p)
{
    for (int i = 0; i < ITERATIONS; i++)
    {
        p.xy = abs(p.xy);
        p = hReflect(p, M[2]);
        p = hReflect(p, M[3]);
    }
    return p;
}

float dist2Vertex(vec4 p, float r)
{
    float ca = -hDot(p, v0);
    float sa = sqrt(ca * ca - 1.0);
    return hDist2eDist(ca * cVR - sa * sVR, sa * cVR - ca * sVR, r);
}

float dist2Segment(vec4 p, vec4 n, float r)
{
    float pn = hDot(p, n), pv = hDot(p, v0), nv = hDot(n, v0);
    float det = -1.0 / (1.0 + pn * pn);
    float alpha = det * (pv - pn * nv);
    float beta = -det * (pn + pv * nv);
    vec4 pmin = hNormalize(alpha * v0 + min(0.0, beta) * n);
    float ca = -hDot(p, pmin), sa = sqrt(ca * ca - 1.0);
    return hDist2eDist(ca * cSR - sa * sSR, sa * cSR - ca * sSR, r);
}

float dist2Segments(vec4 p, float r)
{
    float res = 1.0;
    for (int i = 0; i < 4; i++)
    {
        res = min(res, dist2Segment(p, M[i], r));
    }
	return res;
}

float DE(vec3 p)
{
    float r = length(p);
    vec4 p4 = stereoInverse(p);
    p4 = fold(p4);
    return max(r - CSphRad, min(dist2Vertex(p4, r), dist2Segments(p4, r)));
}

vec3 calcNormal(vec3 p)
{
    const vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
			  DE(p + e.xyy) - DE(p - e.xyy),
			  DE(p + e.yxy) - DE(p - e.yxy),
			  DE(p + e.yyx) - DE(p - e.yyx)));
}

float trace(vec3 ro, vec3 rd)
{
    float t = MIN_TRACE_DIST;
    float h;
    for (int i = 0; i < MAX_TRACE_STEPS; i++)
    {
        h = DE(ro + rd * t);
        if (h < PRECISION * t || t > MAX_TRACE_DIST)
            return t;
        t += h;
    }
    return -1.0;
}

float softShadow(vec3 ro, vec3 rd, float tmin, float tmax, float k)
{
    float res = 1.0;
    float t = tmin;
    for (int i = 0; i < 10; i++)
    {
        float h = DE(ro + rd * t);
        res = min(res, k * h / t);
        t += clamp(h, 0.01, 0.05);
        if (h < 0.001 || t > tmax)
            break;
    }
    return clamp(res, 0.0, 1.0);
}

float calcAO(vec3 p, vec3 n)
{
    float occ = 0.0;
    float sca = 1.0;
    for (int i = 0; i < 5; i++)
    {
        float h = 0.01 + 0.15 * float(i) / 4.0;
        float d = DE(p + h * n);
        occ += (h - d) * sca;
        sca *= 0.7;
    }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}

vec3 baseColor(vec3 p)
{
    float r = length(p);
    vec4 p4 = stereoInverse(p);
    p4 = fold(p4);
    float dScene = dist2Vertex(p4, r);
    int obj = -1;
    for (int i = 0; i < 4; i++)
        {
            float dSeg = dist2Segment(p4, M[i], r);
            if (dSeg < dScene)
            {
                dScene = dSeg;
                obj = i;
            }
        }
	return obj == -1 ? vertexColor : segmentColors[obj];
}

vec3 render(vec3 ro, vec3 rd, vec3 lp)
{
    vec3 bg = vec3(0.0);
    vec3 col = bg;
    float dist = trace(ro, rd);
    if (dist >= 0.0)
	{

        vec3 pos = ro + rd * dist;
        vec3 nor = calcNormal(pos);
        vec3 ld = lp - pos;

        vec3 objCol = baseColor(pos);
        float lDist = max(length(ld), 0.001);
        ld /= lDist;
        float atten = 1.0 / ( 1.0 + lDist * lDist * 0.05);
        float ambient = 0.3;
        float diffuse = clamp(dot(nor, ld), 0.0, 1.0);
        float specular = max(0.0, dot(reflect(-ld, nor), -rd));
	    specular = pow(specular, 40.0);

        float shadow = softShadow(pos, ld, 0.02, lDist, 32.0);
        float ao = calcAO(pos, nor);

        col = objCol * (vec3(1.0, 0.97, 0.92) * diffuse * 0.4 + ambient) + vec3(1.0, 0.9, 0.92) * specular * 2.0;
	    col *= atten * ao * shadow;
    }
    col = mix(col, bg, smoothstep(0.0, 0.95, dist / 3.0));
    return col;
}

mat3 viewMatrix(vec3 camera, vec3 lookat, vec3 up)
{
    vec3 f = normalize(lookat - camera);
    vec3 r = normalize(cross(f, up));
    vec3 u = normalize(cross(r, f));
    return mat3(r, u, -f);
}

void rot2d(inout vec2 p, float a) { p = cos(a) * p + sin(a) * vec2(p.y, -p.x); }

void transform(inout vec3 p)
{
    if (iMouse.x > 0.0)
    {
        float theta = -(2.0 * iMouse.y - iResolution.y) / iResolution.y * PI;
        float phi = -(2.0 * iMouse.x - iResolution.x) / iResolution.x * PI;
        rot2d(p.yz, -theta);
        rot2d(p.xz, phi);
    }
}

void main()
{
    init();
    vec3 camera = vec3(0.0);
    vec3 lookat = vec3(1.0, 0.4, 1.0);
    vec3 up = vec3(0.0, 1.0, 0.0);
    mat3 M = viewMatrix(camera, lookat, up);
    vec3 tot = vec3(0.0);
        for (int ii = 0; ii < AA; ii ++)
	    {
	        for (int jj = 0; jj < AA; jj++)
		        {
                    // map uv to (-1, 1) and adjust aspect ratio
                    vec2 offset = vec2(float(ii), float(jj)) / float(AA);
                    vec2 uv = (gl_FragCoord.xy + offset) / iResolution.xy;
                    uv = 2.0 * uv - 1.0;
                    uv.x *= iResolution.x / iResolution.y;
                    vec3 ro = camera;
                    vec3 rd = M * normalize(vec3(uv, -FOV_DIST));
                    vec3 lig = ro + rd * 0.001 + vec3(0.0, 0.01, 0.0);
                    transform(ro);
                    transform(rd);
                    transform(lig);
                    vec3 col = render(ro, rd, lig);
                    tot += col;
                }
	    }
    tot /= float(AA * AA);
    FinalColor = vec4(tot, 1.0);
}
