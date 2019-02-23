#define FOLDING_NUMBER  8

const float fovdist = 2.0;
const vec4 param_min = vec4(-1.4661, -1.1076, -1.1844, 1.8886);
const vec4 param_max = vec4(3.7324, 1.1972, 1.1204, 2.4136);

float sdSponge(vec3 z)
{
    z *= 5.0;
    //folding
    for(int i = 0; i < 4; i++)
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
    return dis *0.2 * pow(3.0, -3.0); 
}

float DE(vec3 p)
{
    float k, r2;
    float scale = 1.0;
    float orb = 1.0;
    for (int i = 0; i < FOLDING_NUMBER; i++)
	{
	    p = 2.0 * clamp(p, param_min.xyz, param_max.xyz) - p;
	    r2 = dot(p, p);
	    k = max(param_min.w / r2, 1.0);
	    p *= k;
	    scale *= k;
	}
    p /= scale;
    p *= param_max.w * 10.0;
    return 0.1 * sdSponge(p) / (param_max.w * 10.0);
}

vec3 DE_COLOR(vec3 p)
{
    float k, r2;
    float scale = 1.0;
    float orb = 1e4;
    for (int i = 0; i < FOLDING_NUMBER; i++)
    {
        p = 2.0 * clamp(p, param_min.xyz, param_max.xyz) - p;
	r2 = dot(p, p);
	orb = min(orb, r2);
	k = max(param_min.w / r2, 1.0);
	p *= k;
	scale *= k;
    }
    return vec3(0.0, sqrt(orb), orb);
}

vec3 render2(vec3 ro, vec3 rd, float maxDistAO, float maxDistShadow, vec3 background)
{
    vec3 col;
    vec3 res = trace(ro, rd);
    float t = res.x;
    if (t >= 0.0)
	{
            col = vec3(0.94, 0.93, 0.90); // silver taken from POV-Ray
	    vec3 pos = ro + rd * t;
	    vec3 nor = calcNormal(pos);
	    vec3 ref = reflect(rd, nor);
	    vec3 lig = normalize(vec3(1.0));
	    vec3 hal = normalize(lig - rd);
	    float occ = calcAO(pos, nor, maxDistAO);
	    float sha = 0.5 + 0.5 * softShadow(pos, lig, maxDistShadow);
	    float amb = 0.3;
	    float dif = clamp(dot(nor, lig), 0.0, 1.0);
	    float bac = clamp(dot(nor, normalize(vec3(-lig.x, 0.0, -lig.z))), 0.0, 1.0) * clamp(1.0 - pos.y, 0.0, 1.0);
	    float dom = smoothstep(-0.1, 0.1, ref.y);
	    float fre = clamp(1.0 + dot(nor, rd), 0.0, 1.0);
	    fre *= fre;
	    float spe = pow(clamp(dot(ref, lig), 0.0, 0.7), 60.0);
	    vec3 lin = vec3(0.5)
		+ 1.5 * sha * dif * vec3(1.0, 0.8, 0.55)
		+ 4.0 * spe * vec3(1.0, 0.9, 0.7) * dif
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
	    vec3 camera = vec3(1.0, -1.0, 0.6);
	    vec3 lookat = vec3(0.0);
	    vec3 up = vec3(0.0, 0.0, 1.0);
	    // set camera
	    vec3 ro = camera;
	    ro.xy = R(ro.xy, T);
	    mat3 M = viewMatrix(ro, lookat, up);
	    // put screen at distance fovdist in front of the camera
	    vec3 rd = M * normalize(vec3(uv, -fovdist));
	    
	    vec3 col = render2(ro, rd, 0.05, 1.0, vec3(0.08, 0.16, 0.34));
	    tot += col;
        }
    }
    tot /= float(AA * AA);
    FinalColor = vec4(tot, 1.0);
}
