out vec4 FinalColor;

#define FOLDING_NUMBER  7

const vec4 param_min = vec4(-0.8323, -0.694, -0.5045, 0.8067);
const vec4 param_max = vec4(0.8579, 1.0883, 0.8937, 0.9411);


float DE(vec3 p)
{
    float k, r2;
    float scale = 1.0;
    float orb = 1.0;
    for (int i = 0; i < FOLDING_NUMBER; i++)
	{
	    p = 2.0 * clamp(p, param_min.xyz, param_max.xyz) - p;
	    r2 = dot(p, p);
	    k = max(param_min.w / dot(p, p), 1.0);
	    p *= k;
	    scale *= k;
	}
    float lxy = length(p.xy);
    return 0.5 * max(param_max.w - lxy, lxy * p.z / length(p)) / scale;
}

vec3 DE_COLOR(vec3 p)
{
    float k, r2;
    float scale = 1.0;
    float orb = 1e4;
    for (int i = 0; i < FOLDING_NUMBER; i++)
    {
	p = -1.0 + 2.0*fract(0.5*p+0.5);
	r2 = dot(p, p);
	orb = min(orb, r2);
	k = max(param_min.w / dot(p, p), 1.0);
	p *= k;
	scale *= k;
    }
    return vec3(0.0, 0.25 + sqrt(orb), orb);
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
	    ro.xy = R(ro.xy, T);
	    mat3 M = viewMatrix(ro, lookat, up);
	    // put screen at distance 3 in front of the camera
	    vec3 rd = M * normalize(vec3(uv, -3.0));
	    
	    vec3 col = render(ro, rd, 0.05, 1.0);
	    tot += col;
        }
    }
    tot /= float(AA * AA);
    FinalColor = vec4(tot, 1.0);
}
