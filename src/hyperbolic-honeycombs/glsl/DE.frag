#version 130

uniform vec3  iResolution;
uniform float iTime;
uniform vec3  PQR;
uniform int   AA;

out vec4 FinalColor;


#define MAX_TRACE_STEPS  200
#define MIN_TRACE_DIST   0.01
#define MAX_TRACE_DIST   10.0
#define PRECISION        1e-4
#define PI               3.14159265358979323 
#define T                (iTime * 0.005)

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

float DE(vec3 p);

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
