#version 130

uniform vec3        iResolution;
uniform float       iTime;
uniform float       zoom;
uniform samplerCube iChannel0;

out vec4 FinalColor;

float k = 0.1;

#define K2 ((1.0 - k) / 2.0)
#define K3 (sqrt(2.0) * 0.5 - K2)


float tile0(vec2 uv) {
    float v = length(uv) - K3;
    float w = K2 - length(vec2(abs(uv.x) - 0.5, uv.y - 0.5));
    return mix(v, w, step(abs(uv.x), uv.y));
}

float tile1(vec2 uv) {
    return abs(length(uv - 0.5) - 0.5) - k * 0.5;
}

float tile2(vec2 uv) {
    return abs(uv.x) - k * 0.5;
}

float tile3(vec2 uv) {
    return max(-uv.x - k * 0.5, K2 - length(vec2(uv.x - 0.5, abs(uv.y) - 0.5)));
}

float tile4(vec2 uv) {
    return K2 - length(vec2(abs(uv.x) - 0.5, abs(uv.y) - 0.5));
}

float tile(vec2 uv, int tile) {
    switch(tile) {
        case 0: return 1.414;
        case 1: return max(tile0(uv), 0.15 - length(uv));
        case 2: return tile0(uv.yx);
        case 3: return tile1(uv);
        case 4: return tile0(vec2(uv.x, -uv.y));
        case 5: return tile2(uv);
        case 6: return tile1(vec2(uv.x, -uv.y));
        case 7: return tile3(uv);
        case 8: return tile0(vec2(uv.y, -uv.x));
        case 9: return tile1(vec2(-uv.x, uv.y));
        case 10: return tile2(uv.yx);
        case 11: return tile3(uv.yx);
        case 12: return tile1(vec2(-uv.x, -uv.y));
        case 13: return tile3(vec2(-uv.x, uv.y));
        case 14: return tile3(vec2(-uv.y, uv.x));
        case 15: return tile4(uv);
    }
}

#define HASHSCALE1 0.1031

float hash(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * HASHSCALE1);
    p3 += dot(p3, p3.yzx + 19.19);
    return fract((p3.x + p3.y) * p3.z);
}

float map(vec2 uv) {
    int b = 0;
    uv += 0.5;
    vec2 id = floor(uv);
    if(hash(id) >= 0.5)
        b += 1;
    if(hash(-id) >= 0.5)
        b += 8;
    if(hash(id - vec2(0.0, 1.0)) >= 0.5)
        b += 4;
    if(hash(-(id + vec2(1.0, 0.0))) >= 0.5)
        b += 2;
    return tile(fract(uv) - 0.5, b);
}

vec2 rotate(vec2 uv, float a) {
    float co = cos(a);
    float si = sin(a);
    return uv * mat2(co, si, -si, co);
}

float height(vec2 uv) {
    float r = map(uv) - 0.1;
    return sqrt(0.01 - min(r * r, 0.01));
}

void main() {
    vec2 uv = gl_FragCoord.xy / iResolution.xy;
    uv = uv * 2.0 - 1.0;
    uv.x *= iResolution.x / iResolution.y;
    uv = rotate(uv, iTime * 0.1);
    vec3 rd = normalize(vec3(uv, 1.66));

    float scale = zoom + sin(iTime * 0.5);
    uv *= scale;
    uv += iTime;

    vec2 h = vec2(0.01, 0.0);
    float v = map(uv);
    float c0 = height(uv);
    float c1 = height(uv + h.xy);
    float c2 = height(uv + h.yx);

    vec3 color = vec3(1.0) * smoothstep(0.0, 4.0 / iResolution.y, min(v, abs(v - 0.2) - 0.01) / scale);
    vec3 normal = normalize(vec3(c0 - c1, h.x, c0 - c2));
    vec3 lightDir = normalize(vec3(-0.5, 0.5, 0.1));
    vec3 bounce = reflect(rd, normal);
    color *= dot(normal, lightDir);
    color *= mix(vec3(1.0, 0.7, 0.5), vec3(0.2, 0.5, 1.0), smoothstep(0.0, 2.0 / iResolution.y, min(v, abs(v - 0.1) - 0.1) / scale));
    color *= 3.0 * texture(iChannel0, bounce).xyz;
    color = sqrt(color);
    FinalColor = vec4(color, 1.0);
}
