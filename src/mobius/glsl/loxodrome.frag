#version 130

uniform vec3          iResolution;
uniform float         iTime;
uniform vec4          iMouse;
uniform sampler2D     iTexture;
uniform int           AA;

out vec4 FinalColor;

#define MAX_TRACE_STEPS  50
#define MIN_TRACE_DIST   0.01
#define MAX_TRACE_DIST   10.0
#define PI 3.14159265358979

mat3 viewMatrix(vec3 camera, vec3 lookat, vec3 up) {
    vec3 f = normalize(lookat - camera);
    vec3 r = normalize(cross(f, up));
    vec3 u = normalize(cross(r, f));
    return mat3(r, u, -f);
}

// distance between two points in polar coordinate system
// by the law of cosines
float polarDist(vec2 a, vec2 b) {
    return sqrt(a.x * a.x + b.x * b.x - 2 * a.x * b.x * cos(a.y - b.y));
}

float inverseMix(float a, float b, float x) {
    return (x - a) / (b - a);	
}

vec2 rotate2d(vec2 v, float a) { 
    return vec2(v.x * cos(a) - v.y * sin(a), v.y * cos(a) + v.x * sin(a)); 
}

vec3 rectToSpher(vec3 v) {
    float r = length(v);
    float phi = atan(v.z, v.x);
    phi += 2.0 * PI * step(0.0, phi);
    float theta = atan(v.y, length(v.xz));
    return vec3(r, phi, theta);
}

float secIntegral(float x) {
    return log(1.0 / cos(x) + tan(x));
}

float invSecIntegral(float x) {
    return acos(2.0 / (exp(-x) + exp(x))) * sign(x);
}

float floorCustom(float x, float c) {
    return floor(x / c) * c;	
}

float ceilCustom(float x, float c) {
    return ceil(x / c) * c;	
}

float sdLoxodrome(vec3 p, float twist, float rotSymm, float thickness) {
    vec3 s = rectToSpher(p);
    s.y += iTime;
    float offset = thickness * cos(s.z);
    vec2 s1 = vec2(1.0 - offset, invSecIntegral((ceilCustom(secIntegral(s.z) * twist - s.y, PI * 2.0 / rotSymm) + s.y) / twist));
    vec2 s2 = vec2(1.0 - offset, invSecIntegral((floorCustom(secIntegral(s.z) * twist - s.y, PI * 2.0 / rotSymm) + s.y) / twist));
    float res = min(polarDist(s.xz, s1), polarDist(s.xz, s2));
    res -= offset;
    return res;
}

float sdCylinder(vec3 p, vec2 c) {
    return max(length(p.xy) - c.x, abs(p.z) - c.y);
}

float DE(vec3 p) {
    float wall = -p.z + 1.5;
    float loxodrome = sdLoxodrome(p - vec3(0.0, 0.0, 0.0), 2.0, 4.0, 0.075);
    return min(wall, loxodrome);
}

float shadowDE(vec3 p) {
    float loxodrome = sdLoxodrome(p - vec3(0.0, 0.0, 0.0), 2.0, 4.0, 0.075);
    float holder = 9001.0;
    return min(holder, loxodrome);
}

float getMaterial(vec3 p) {
    float wall = -p.z + 1.0;
    float loxodrome = sdLoxodrome(p - vec3(0.0, 0.0, 0.0), 2.0, 4.0, 0.075);
    float holder = 9001.0;
    return step(min(holder, loxodrome), wall);
}

vec3 calcNormal(vec3 p) {
    const vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
			  DE(p + e.xyy) - DE(p - e.xyy),
			  DE(p + e.yxy) - DE(p - e.yxy),
			  DE(p + e.yyx) - DE(p - e.yyx)));
}

vec3 castRay(vec3 pos, vec3 dir, float treshold) {
    for (int i = 0; i < MAX_TRACE_STEPS; i++) {
        float dist = DE(pos);
        if (abs(dist) < treshold) break;
        pos += dist * dir;
    }
    return pos;
}

float castSoftShadowRay(vec3 pos, vec3 lightPos) {
    const float k = 0.005;
    float res = 1.0;
    vec3 rayDir = normalize(lightPos - pos);
    float maxDist = length(lightPos - pos);    
    vec3 rayPos = pos + 0.01 * rayDir;
    float distAccum = 0.1;
	
    for (int i = 1; i <= 30; i++) {
        rayPos = pos + rayDir * distAccum;
        float dist = shadowDE(rayPos);
        float penumbraDist = distAccum * k;
        res = min(res, inverseMix(-penumbraDist, penumbraDist, dist));
        distAccum += (dist + penumbraDist) * 0.5;
        distAccum = min(distAccum, maxDist);
    }
    res = max(res, 0.0);
    return res;
}

float lightPointDiffuseSoftShadow(vec3 pos, vec3 lightPos, vec3 normal) {
    vec3 lightDir = normalize(lightPos - pos);
    float lightDist = length(lightPos - pos);
    float color = max(dot(normal, lightDir), 0.0) / (lightDist * lightDist);
    if (color > 0.00) color *= castSoftShadowRay(pos, lightPos);
    return max(0.0, color);
}

void main() {
    vec4 mousePos = (iMouse / iResolution.xyxy) * 2.0 - 1.0;
    mousePos *= vec2(PI / 2.0, PI / 2.0).xyxy;
    if (iMouse.zw == vec2(0.0)) mousePos.xy = vec2(0.5, -0.2);	
    vec2 screenPos = (gl_FragCoord.xy / iResolution.xy) * 2.0 - 1.0;
    vec3 cameraPos = vec3(0.0, 0.0, -8.0);	
    vec3 cameraDir = vec3(0.0, 0.0, 1.0);
    vec3 planeU = vec3(1.0, 0.0, 0.0);
    vec3 planeV = vec3(0.0, iResolution.y / iResolution.x * 1.0, 0.0);
    vec3 rayDir = normalize(cameraDir + screenPos.x * planeU + screenPos.y * planeV);
    
    cameraPos.yz = rotate2d(cameraPos.yz, mousePos.y);
    rayDir.yz = rotate2d(rayDir.yz, mousePos.y);
    
    cameraPos.xz = rotate2d(cameraPos.xz, mousePos.x);
    rayDir.xz = rotate2d(rayDir.xz, mousePos.x);
    
    vec3 rayPos = castRay(cameraPos, rayDir, 0.01);
    vec3 normal = calcNormal(rayPos);
    
    float material = getMaterial(rayPos);
    
    vec3 color;
    if (material == 0.0) color = pow(texture(iTexture, gl_FragCoord.xy/iResolution.xy).rgb, vec3(2.2));
    if (material == 1.0) color = vec3(0.05);
	
    color *= 32.0 * lightPointDiffuseSoftShadow(rayPos, vec3(0.0, 0.0, -0.6), normal) + 0.05 * smoothstep(10.0, 0.0, length(rayPos));
    color = pow(color, vec3(1.0 / 2.2));	
    FinalColor = vec4(color, 1.0);
}
