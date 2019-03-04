#version 130

uniform vec3  iResolution;
uniform float iTime;
uniform int   AA;

out vec4 FinalColor;


#define FOV_DIST         3.0
#define FOLDING_NUMBER   7
#define MAX_TRACE_STEPS  200
#define MIN_TRACE_DIST   0.01
#define MAX_TRACE_DIST   10.0
#define PRECISION        1e-4
#define PI               3.14159265358979323
#define T                (iTime * 0.005)


const vec4 param_min = vec4(-0.8323, -0.694, -0.5045, 0.8067);
const vec4 param_max = vec4(0.8579, 1.0883, 0.8937, 0.9411);


// view to world transformation
mat3 viewMatrix(vec3 camera, vec3 lookat, vec3 up)
{
    vec3 f = normalize(lookat - camera);
    vec3 r = normalize(cross(f, up));
    vec3 u = normalize(cross(r, f));
    return mat3(r, u, -f);
}

// 2D rotatation
void R(inout vec2 p, float a)
{
    p = cos(a) * p + sin(a) * vec2(p.y, -p.x);
}

vec2 DE(vec3 p)
{
    float k1, k2, rp2, rq2;
    float scale = 1.0;
    float orb = 1e4;
    vec3 q = p;
    for (int i = 0; i < FOLDING_NUMBER; i++)
	    {
            p = 2.0 * clamp(p, param_min.xyz, param_max.xyz) - p;
            q = 2.0 * fract(0.5 * q + 0.5) - 1.0;
            rp2 = dot(p, p);
            rq2 = dot(q, q);
            k1 = max(param_min.w / rp2, 1.0);
            k2 = max(param_min.w / rq2, 1.0);
            p *= k1;
            q *= k2;
            scale *= k1;
            orb = min(orb, rq2);
        }
    float lxy = length(p.xy);
    return vec2(0.5 * max(param_max.w - lxy, lxy * p.z / length(p)) / scale,
                0.25 + sqrt(orb));
}

vec3 calcNormal(vec3 p)
{
    const vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
			  DE(p + e.xyy).x - DE(p - e.xyy).x,
			  DE(p + e.yxy).x - DE(p - e.yxy).x,
			  DE(p + e.yyx).x - DE(p - e.yyx).x));
}

vec2 trace(vec3 ro, vec3 rd)
{
    float t = MIN_TRACE_DIST;
    vec2 h;
    for (int i = 0; i < MAX_TRACE_STEPS; i++)
        {
            h = DE(ro + rd * t);
            if (h.x < PRECISION * t || t > MAX_TRACE_DIST)
                return vec2(t, h.y);
            t += h.x;
        }
    return vec2(-1.0, 0.0);
}

float softShadow(vec3 ro, vec3 rd, float tmin, float tmax, float k)
{
    float res = 1.0;
    float t = tmin;
    for (int i = 0; i < 30; i++)
        {
            float h = DE(ro + rd * t).x;
            res = min(res, k * h / t);
            t += clamp(h, 0.01, 0.1);
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
            float d = DE(p + h * n).x;
            occ += (h - d) * sca;
            sca *= 0.9;
        }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}

vec3 render(vec3 ro, vec3 rd, vec3 lig)
{
    vec3 background = vec3(0.08, 0.16, 0.32);
    vec3 col = background;
    vec2 res = trace(ro, rd);
    float t = res.x;
    if (t >= 0.0)
	    {
            col = 0.5 + 0.5 * cos(2.0 * PI * res.y + vec3(0.0, 1.0, 2.0));
            vec3 pos = ro + rd * t;
            vec3 nor = calcNormal(pos);
            vec3 ref = reflect(rd, nor);

            float occ = calcAO(pos, nor);
            float amb = clamp(0.2 + 0.3 * nor.y, 0.0, 0.3);
            float dif = clamp(dot(nor, lig), 0.0, 1.0);
            float fre = pow(clamp(1.0 + dot(nor, rd), 0.0, 1.0), 2.0);
            float spe = pow(clamp(dot(ref, lig), 0.0, 1.0), 16.0);
            dif *= 0.4 + 0.6 * softShadow(pos, lig, 0.02, 3.0, 12.0);

            vec3 lin = vec3(0.5);
            lin += 1.8 * dif * vec3(1.0, 0.8, 0.55);
            lin += 2.0 * spe * vec3(1.0, 0.9, 0.7) * dif;
            lin += 0.5 * amb * vec3(0.4, 0.6, 1.0) * occ;
            lin += 0.25 * fre * vec3(1.0) * occ;

            col *= lin;
            float atten = 1.0 / (1.0 + t * t * 0.05);
            col *= atten;
            col = mix(col, background, smoothstep(0.0, 0.95, t / MAX_TRACE_DIST));
        }
    return col;
}

void main()
{
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
                    vec3 camera = vec3(1.07, 1.04, 0.87);
                    vec3 lookat = vec3(-0.687, -0.63, -0.35);
                    vec3 up = vec3(0.0, 0.0, 1.0);
                    // set camera
                    vec3 ro = camera;
                    R(ro.xy, T);
                    mat3 M = viewMatrix(ro, lookat, up);
                    // put screen at distance FOV_DISt in front of the camera
                    vec3 rd = M * normalize(vec3(uv, -FOV_DIST));

                    vec3 lig = normalize(vec3(0.2, 0.7, 0.6));
                    vec3 col = render(ro, rd, lig);
                    tot += col;
                }
	    }
    tot /= float(AA * AA);
    FinalColor = vec4(tot, 1.0);
}
