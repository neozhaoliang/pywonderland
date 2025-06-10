#version 130

uniform vec2 iResolution;
uniform vec2 center;

uniform float iTime;
uniform float zoom;

uniform vec2 pointsA[trail_length];
uniform vec2 pointsB[trail_length];
uniform vec2 pointsC[trail_length];

out vec4 fragColor;

const vec3 colA = vec3(0.1, 0.9, 0.1);
const vec3 colB = vec3(0.9, 0.05, 0.05);
const vec3 colC = vec3(0.02, 0.02, 0.8);

const float lumA = dot(colA, vec3(0.299, 0.587, 0.114));
const float lumB = dot(colB, vec3(0.299, 0.587, 0.114));
const float lumC = dot(colC, vec3(0.299, 0.587, 0.114));

const float fade = 0.025;

vec3 glowPoint(vec2 p, vec2 center, vec3 col, float lum, float strength) {
    float d = max(abs(length(p - center)), 1e-5);
    d = pow(strength / d, 2.);
    d /= lum;
    return 1.0 - exp(-d * col);
}

vec2 sdSegment(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a;
    vec2 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    float d = length(pa - ba * h);
    d = max(abs(d), 1e-5);
    return vec2(d, h);
}

void mainImage(in vec2 fragCoord, out vec4 fragColor) {
    vec2 uv = (2.0 * fragCoord - iResolution.xy) / iResolution.y;
    uv *= zoom;
    uv -= center;
    vec3 color = vec3(0.0);

    float dA = 1e5, dB = 1e5, dC = 1e5;
    for (int i = 0; i < trail_length - 1; i++) {
        vec2 fA = sdSegment(uv, pointsA[i], pointsA[i + 1]);
        vec2 fB = sdSegment(uv, pointsB[i], pointsB[i + 1]);
        vec2 fC = sdSegment(uv, pointsC[i], pointsC[i + 1]);
        float c1 = 1. - (fA.y + float(i)) / float(trail_length);
        float c2 = 1. - (fB.y + float(i)) / float(trail_length);
        float c3 = 1. - (fC.y + float(i)) / float(trail_length);

        dA = min(dA, fA.x + fade * c1);
        dB = min(dB, fB.x + fade * c2);
        dC = min(dC, fC.x + fade * c3);
    }
    
    const float trail_strength = 0.008;

    dA = pow(trail_strength / dA, 4.) / lumA;
    dB = pow(trail_strength / dB, 4.) / lumB;
    dC = pow(trail_strength / dC, 4.) / lumC;

    color += 1. - exp(-colA * dA);
    color += 1. - exp(-colB * dB);
    color += 1. - exp(-colC * dC);

    vec2 endA = pointsA[trail_length - 1];
    vec2 endB = pointsB[trail_length - 1];
    vec2 endC = pointsC[trail_length - 1];

    const float particle_strength = 0.04;
    color += glowPoint(uv, endA, colA, lumA, particle_strength);
    color += glowPoint(uv, endB, colB, lumB, particle_strength);
    color += glowPoint(uv, endC, colC, lumC, particle_strength);

    fragColor = vec4(pow(clamp(color, 0.0, 1.0), vec3(0.4545)), 1.0);
}

void main() { mainImage(gl_FragCoord.xy, fragColor); }
