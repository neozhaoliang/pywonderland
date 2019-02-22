#define FOLDING_NUMBER  8


float DE(vec3 p)
{
    float k, r2;
    float scale = 1.0;
    for (int i = 0; i < FOLDING_NUMBER; i++)
	{
	    p = 2.0 * fract(0.5 * p + 0.5) - 1.0;
	    r2 = dot(p, p);
	    k = 1.2 / r2;
	    p *= k;
	    scale *= k;
	}
    return 0.25 * abs(p.y) / scale;
}
    
vec3 DE_COLOR(vec3 p)
{
    float k, r2;
    float scale = 1.0;
    float orb = 1e4;
    for (int i = 0; i < FOLDING_NUMBER; i++)
	{
	    p = 2.0 * fract(0.5 * p + 0.5) - 1.0;
	    r2 = dot(p, p);
	    orb = min(orb, r2);
	    k = max(1.2 / r2, 1.0);
	    p *= k;
	    scale *= k;
	}
    return vec3(0.0, 0.2 + k * cos(PI * 0.5 * length(p * 12.0)) * sqrt(orb), orb);
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
		    vec3 camera = vec3(1.0, 1.4, -1.58) * 0.4;
		    vec3 lookat = vec3(0.36, 0.3, -0.03);
		    vec3 up = vec3(0.0, 1.0, 0.0);
		    // set camera
		    vec3 ro = camera;
		    ro.xz = R(ro.xz, T);
		    mat3 M = viewMatrix(ro, lookat, up);
		    // put screen at distance 3 in front of the camera
		    vec3 rd = M * normalize(vec3(uv, -3.0));
	    
		    vec3 col = render(ro, rd, 0.05, 1.0, vec3(0.08, 0.16, 0.35));
		    tot += col;
		}
	}
    tot /= float(AA * AA);
    FinalColor = vec4(tot, 1.0);
}
