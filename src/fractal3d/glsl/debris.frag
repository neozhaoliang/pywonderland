#version 130

uniform vec3  iResolution;
uniform float iTime;
uniform int   AA;

out vec4 FinalColor;


#define FOV_DIST           3.0
#define BULB_ITERATIONS    8
#define SPONGE_ITERATIONS  10
#define MAX_TRACE_STEPS    200
#define MIN_TRACE_DIST     0.01
#define MAX_TRACE_DIST     10.0
#define PRECISION          1e-4
#define PI                 3.14159265358979323
#define T                  (iTime * 0.005)

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

float mandelbulb(vec3 p)
{
    p /= 1.192;
    p.xyz = p.xzy;
    vec3 z = p;
    vec3 dz = vec3(0.0);
    float dr = 1.0;
    float power = 8.0;
    float r, theta, phi;
    for (int i = 0; i < BULB_ITERATIONS; i++)
        {
            r = length(z);
            if (r > 2.0)
                break;
            float theta = atan(z.y / z.x);
            float phi = asin(z.z / r);
            dr = pow(r, power - 1.0) * power * dr + 1.0;
            r = pow(r, power);
            theta = theta * power;
            phi = phi * power;
            z = r * vec3(cos(theta) * cos(phi), cos(phi) * sin(theta), sin(phi)) + p;
        }
    return 0.5 * log(r) * r / dr;
}

float sdSponge(vec3 z)
{
    //folding
    for(int i = 0; i < SPONGE_ITERATIONS; i++)
        {
            z = abs(z);
            z.xy = (z.x < z.y) ? z.yx : z.xy;
            z.xz = (z.x < z.z) ? z.zx : z.xz;
            z.zy = (z.y < z.z) ? z.yz : z.zy;	 
            z = z * 3.0 - 2.0;
            z.z += (z.z < -1.0) ? 2.0 : 0.0;
        }
    //distance to cube
    z = abs(z) - vec3(1.0);
    float dis = min(max(z.x, max(z.y, z.z)), 0.0) + length(max(z, 0.0)); 
    //scale cube size to iterations
    return dis * 0.6 * pow(3.0, -float(SPONGE_ITERATIONS)); 
}

float DE(vec3 p)
{
    float d1 = mandelbulb(p);
    float d2 = sdSponge(p);
    return max(d1, d2);
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
    for (int i = 0; i < 30; i++)
        {
            float h = DE(ro + rd * t);
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
            float d = DE(p + h * n);
            occ += (h - d) * sca;
            sca *= 0.9;
        }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}

// https://www.shadertoy.com/view/4dSfRc
vec3 render(vec3 ro, vec3 rd, vec3 lig)
{
    vec3 background = vec3(0.08, 0.16, 0.32);
    vec3 col = background;
    float t = trace(ro, rd);
    if (t >= 0.0)
	    {
            col = vec3(0.9);
            vec3 pos = ro + rd * t;
            vec3 nor = calcNormal(pos);
            vec3 ref = reflect(rd, nor);

            float occ = calcAO(pos, nor);
            float amb = 0.3;
            float dif = clamp(dot(nor, lig), 0.0, 1.0);
            float bac = clamp(dot(nor, normalize(vec3(-lig.x, 0.0, -lig.z))), 0.0, 1.0 ) * clamp(1.0 - pos.y, 0.0, 1.0);
            float dom = smoothstep(-0.1, 0.1, ref.y);
            float fre = pow(clamp(1.0 + dot(nor, rd), 0.0, 1.0), 2.0);
            float spe = pow(clamp(dot(ref, lig), 0.0, 1.0), 16.0);
            dif *= softShadow(pos, lig, 0.02, 5.0, 16.0);
            dom *= softShadow(pos, ref, 0.02, 5.0, 16.0);

            vec3 lin = vec3(0.5);
            lin += 1.5 * dif * vec3(1.0, 0.8, 0.55);
            lin += 4.0 * spe * vec3(1.0, 0.9, 0.7) * dif;
            lin += 0.3 * amb * vec3(0.4, 0.6, 1.0) * occ;
            lin += 0.5 * bac * vec3(0.25) * occ;
            lin += 0.5 * dom * vec3(0.4, 0.6, 1.0) * occ;
            lin += 0.25 * fre * vec3(1.0) * occ;

            col *= lin;

            float atten = 1.0 / (1.0 + t * t * 0.1);
            col *= atten * occ;
            col = mix(col, background, smoothstep(0.0, 0.95, t / MAX_TRACE_DIST));
        }
    return sqrt(col);
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
                    vec3 camera = vec3(4.0) / (min(3.5, 1.0 + pow(2.0, T)));
                    vec3 lookat = vec3(0.0);
                    vec3 up = vec3(0.0, 1.0, 0.0);
                    // set camera
                    vec3 ro = camera;
                    R(ro.xz, T);
                    mat3 M = viewMatrix(ro, lookat, up);
                    // put screen at distance FOV_DISt in front of the camera
                    vec3 rd = M * normalize(vec3(uv, -FOV_DIST));

                    vec3 lig = normalize(vec3(1.0, 2.0, 1.0));
                    vec3 col = render(ro, rd, lig);
                    tot += col;
		        }
	    }
    tot /= float(AA * AA);
    FinalColor = vec4(tot, 1.0);
}
