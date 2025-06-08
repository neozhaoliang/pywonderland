#version 130

uniform vec2 iResolution;
uniform vec2 center;

uniform float iTime;
uniform float zoom;

uniform vec2 pointsA[trail_length];
uniform vec2 pointsB[trail_length];
uniform vec2 pointsC[trail_length];

out vec4 fragColor;

const vec3 col1 = vec3(0.1, 1.0, 0.1);
const vec3 col2 = vec3(0.9, 0.05, 0.05);
const vec3 col3 = vec3(0.02, 0.02, 0.8);

const float fade = 0.025;

vec3 glowPoint(vec2 p, vec2 center, vec3 col, float strength) {
    float d = max(abs(length(p - center)), 1e-5);
    d = pow(strength / d, 2.);
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
    const float trail_strength = 0.01;
    color += 1. - exp(-col1 * pow(trail_strength * 0.67 / dA, 4.));
    color += 1. - exp(-col2 * pow(trail_strength * 1. / dB, 4.));
    color += 1. - exp(-col3 * pow(trail_strength * 1.5 / dC, 4.));

    vec2 endA = pointsA[trail_length - 1];
    vec2 endB = pointsB[trail_length - 1];
    vec2 endC = pointsC[trail_length - 1];

    const vec3 particle_strengths = vec3(0.02, 0.08, 0.1);
    color += glowPoint(uv, endA, col1, particle_strengths.x);
    color += glowPoint(uv, endB, col2, particle_strengths.y);
    color += glowPoint(uv, endC, col3, particle_strengths.z);

    fragColor = vec4(pow(clamp(color, 0.0, 1.0), vec3(0.4545)), 1.0);
}

void main() { mainImage(gl_FragCoord.xy, fragColor); }
