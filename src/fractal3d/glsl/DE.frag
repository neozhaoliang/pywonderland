#version 130

uniform vec3  iResolution;
uniform float iTime;
uniform int   AA;

out vec4 FinalColor;


#define MAX_TRACE_STEPS  200
#define MIN_TRACE_DIST   0.01
#define MAX_TRACE_DIST   10.0
#define PRECISION        1e-4
#define PI               3.14159265358979323 
#define T                (iTime * 0.005)

// view to world transformation
mat3 viewMatrix(vec3 camera, vec3 lookat, vec3 up)
{
    vec3 f = normalize(lookat - camera);
    vec3 r = normalize(cross(f, up));
    vec3 u = normalize(cross(r, f));
    return mat3(r, u, -f);
}

// 2D rotatation
vec2 R(vec2 p, float a)
{
    return cos(a) * p + sin(a) * vec2(p.y, -p.x);
}

// random functions
float hash1(float seed)
{
    return fract(sin(seed) * 43758.5453123);
}

vec2 hash2(float seed)
{
    return fract(sin(vec2(seed * 43758.5453123,
			  (seed + 0.1) * 22578.1459123)));
}

vec3 randomHemisphereDirection(vec3 n, float seed)
{
    vec2 r = 2.0 * PI * hash2(seed);
    vec3 dr = vec3(sin(r.x) * vec2(sin(r.y), cos(r.y)), cos(r.x));
    float k = dot(dr, n);
    return k == 0.0 ? n : normalize(k * dr);
}

// you must implement the following two functions in the scene fragment file!
float DE(vec3 p);

vec3 DE_COLOR(vec3 p);

vec3 calcNormal(vec3 p)
{
    const vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
			  DE(p + e.xyy) - DE(p - e.xyy),
			  DE(p + e.yxy) - DE(p - e.yxy),
			  DE(p + e.yyx) - DE(p - e.yyx)));
}

float hit(vec3 ro, vec3 rd)
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

vec3 trace(vec3 ro, vec3 rd)
{
    float t = hit(ro, rd);
    if (t > 0.0)
	return vec3(t, DE_COLOR(ro + rd * t).yz);
    return vec3(-1.0, 1.0, 0.0);
}

float calcAO(vec3 ro, vec3 n, float maxDistAO)
{
    float seed = hash1(ro.x * (ro.y * 32.56) + ro.z * 147.2 + ro.y);
    vec3 rd = randomHemisphereDirection(n, seed);
    float d = hit(ro, rd);
    if (d > 0.0)
	return 1.0 - clamp((maxDistAO - d) / maxDistAO, 0.0, 1.0);
    return 1.0;
}

float softShadow(const vec3 ro, const vec3 rd, float maxDistShadow) {
    float seed = hash1(ro.x*(ro.y*32.56)+ro.z*147.2 + ro.y);
    float d = hit(ro, rd);
    if (d > 0.0)
        return smoothstep(0.0, maxDistShadow, d);
    return 1.0;
}

/*
float softShadow(vec3 ro, vec3 rd, float tmin, float tmax, float k)
{
    float res = 1.0;
    float t = tmin;
    for (int i = 0; i < 200; i++)
    {
        float h = DE(ro + rd * t);
        res = min(res, k * h / t);
        t += clamp(h, 0.001, 0.05);
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
        sca *= 0.95;
    }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}
*/

vec3 render(vec3 ro, vec3 rd, float maxDistAO, float maxDistShadow, vec3 background)
{
    vec3 col = vec3(0.0);
    vec3 res = trace(ro, rd);
    float t = res.x;
    if (t >= 0.0)
	{
	    vec3 pos = ro + rd * t;
	    vec3 nor = calcNormal(pos);
	    vec3 ref = reflect(rd, nor);
	    col = 0.5 + 0.5 * cos(6.2831 * res.y + vec3(0.0, 1.0, 2.0));
	    vec3 lig = normalize(vec3(0.2, 0.7, 1.6));
	    vec3 hal = normalize(lig - rd);
	    float occ = calcAO(pos, nor, maxDistAO);
	    float sha = 0.5 + 0.5 * softShadow(pos, lig, maxDistShadow);
	    float amb = clamp(0.2 + 0.5 * nor.y, 0.0, 1.0);
	    float dif = clamp(dot(nor, lig), 0.0, 1.0);
	    float bac = clamp(dot(nor, normalize(vec3(-lig.x, 0.0, -lig.z))), 0.0, 1.0) * clamp(1.0 - pos.y, 0.0, 1.0);
	    float dom = smoothstep(-0.1, 0.1, ref.y);
	    float fre = clamp(1.0 + dot(nor, rd), 0.0, 1.0);
	    fre *= fre;
	    float spe = pow(clamp(dot(ref, lig), 0.0, 1.0), 16.0);
	    vec3 lin = vec3(0.5)
		+ 1.3 * sha * dif * vec3(1.0, 0.8, 0.55)
		+ 2.0 * spe * vec3(1.0, 0.9, 0.7) * dif
		+ 0.5 * occ * (0.4 * amb * vec3(0.4, 0.6, 1.0)
			       + 0.5 * sha * vec3(0.4, 0.6, 1.0)
			       + 0.25 * fre * vec3(1.0));
	    col = col * lin;
	    float lDist = t;
	    float atten = 1.0 / (1.0 + lDist * 0.3);
	    col *= atten * col * occ;
	    col = mix(col, background, smoothstep(0.0, 0.95, t / MAX_TRACE_DIST));
	}
    else
	{
	    col = background;
	}
    return sqrt(col);
}
