"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Periodic Solutions of the Three-Body Problem (2D Animation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script was inspired by this post:

https://www.reddit.com/r/physicsgifs/comments/14db21p/a_few_three_body_periodic_orbits/

The author claims he used Blender and Python, but I thought a lightweight animation
with real-time preview would be better，　so I made the animation below using Vispy
and GLSL.

I've included only two periodic solutions here. More can be found at:

https://observablehq.com/@rreusser/periodic-planar-three-body-orbits

The only things you need to set are the period, the initial positions and velocities.

There are many variables you can tweak to control the visual effect.
For example, `dt` and `trail_length` both affect the length of the trails.
When it comes to controlling the glowing effect of the trails, several variables
in the GLSL shader are also involved. I haven't had time to figure out a universal
set of parameters that work for all solutions, so you might need to experiment and
adjust them manually.
"""

import numpy as np
from vispy import app, gloo
from vispy.io import imsave
from scipy.integrate import solve_ivp


G = m1 = m2 = m3 = 1.0

init_conditions = {
    "figure 8": {
        "period": 6.324449,
        "positions": [(-1, 0), (1, 0), (0, 0)],
        "velocities": [
            (0.347111, 0.532728),
            (0.347111, 0.532728),
            (-2 * 0.347111, -2 * 0.532728),
        ],
    },
    "Broucke　A11": {
        "period": 32.584945,
        "positions": [(0.0132604844, 0), (1.4157286016, 0), (-1.4289890859, 0)],
        "velocities": [(0, 1.054151921), (0, -0.2101466639), (0, -0.8440052572)],
    },
}


def calc_accel(t, y):
    r1, r2, r3, v1, v2, v3 = np.split(y, 6)
    d12 = d21 = np.linalg.norm(r2 - r1) ** 3
    d23 = d32 = np.linalg.norm(r3 - r2) ** 3
    d31 = d13 = np.linalg.norm(r1 - r3) ** 3

    a1 = G * m2 * (r2 - r1) / d12 + G * m3 * (r3 - r1) / d13
    a2 = G * m3 * (r3 - r2) / d23 + G * m1 * (r1 - r2) / d21
    a3 = G * m1 * (r1 - r3) / d31 + G * m2 * (r2 - r3) / d32
    return np.concatenate([v1, v2, v3, a1, a2, a3])


name = "Broucke　A11"
T = init_conditions[name]["period"]
r1_0, r2_0, r3_0 = init_conditions[name]["positions"]
y0 = np.concatenate([r1_0, r2_0, r3_0] + init_conditions[name]["velocities"])
dt = 0.04
num_steps = int(T / dt) + 1
t_eval = np.linspace(0, T, num_steps)

sol = solve_ivp(
    calc_accel, [0, T], y0, t_eval=t_eval, method="RK45", rtol=1e-9, atol=1e-9
)
solution = sol.y.T

r1 = solution[:, 0:2]
r2 = solution[:, 2:4]
r3 = solution[:, 4:6]

trail_length = 600


vertex_shader = """
#version 130
in vec2 position;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
}
"""

fragment_shader = f"""
#version 130

uniform vec2 iResolution;
uniform float iTime;
uniform float zoom;

uniform vec2 pointsA[{trail_length}];
uniform vec2 pointsB[{trail_length}];
uniform vec2 pointsC[{trail_length}];

out vec4 fragColor;

vec3 glowPoint(vec2 p, vec2 center, float radius, vec3 col) {{
    float d = 1.0 / max(abs(length(p - center) - radius), 1e-5);
    d *= .03;
    d = pow(d, 2.);
    return 1.0 - exp(-d * col);
}}

vec2 sdSegment(vec2 p, vec2 a, vec2 b) {{
    vec2 pa = p - a;
    vec2 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    float d = length(pa - ba * h);
    d = max(abs(d), 1e-5);
    return vec2(d, h);
}}



void mainImage(in vec2 fragCoord, out vec4 fragColor) {{
    vec2 uv = (2.0 * fragCoord - iResolution.xy) / iResolution.y;
    uv *= zoom;

    vec3 color = vec3(0.0);
    vec3 col1 = vec3(0.75, 0.9, 0.12);
    vec3 col2 = vec3(1.0, 0.2, 0.13);
    vec3 col3 = vec3(0.1, 0.2, 1.0);

    float radius = 0.03;
    float dA = 1e5, dB = 1e5, dC = 1e5;
    for (int i = 0; i < {trail_length} - 1; i++) {{
        vec2 fA = sdSegment(uv, pointsA[i], pointsA[i+1]);
        vec2 fB = sdSegment(uv, pointsB[i], pointsB[i+1]);
        vec2 fC = sdSegment(uv, pointsC[i], pointsC[i+1]);
        float c1 = 1. - (fA.y + float(i)) /  float({trail_length});
        float c2 = 1. - (fB.y + float(i)) /  float({trail_length});
        float c3 = 1. - (fC.y + float(i)) /  float({trail_length});
        const float fade = 0.025;
        dA = min(dA, fA.x + fade * c1);
        dB = min(dB, fB.x + fade * c2);
        dC = min(dC, fC.x + fade * c3);
    }}

    const float strength = 0.015;
    color += 1. - exp(-col1 * pow(strength/dA, 4.));
    color += 1. - exp(-col2 * pow(strength/dB, 4.));
    color += 1. - exp(-col3 * pow(strength/dC, 4.));

    vec2 endA = pointsA[{trail_length} - 1];
    vec2 endB = pointsB[{trail_length} - 1];
    vec2 endC = pointsC[{trail_length} - 1];
    color += glowPoint(uv, endA, radius, col1);
    color += glowPoint(uv, endB, radius, col2);
    color += glowPoint(uv, endC, radius, col3);
    fragColor = vec4(pow(clamp(color, 0.0, 1.0), vec3(0.45)), 1.0);
}}

void main() {{
    mainImage(gl_FragCoord.xy, fragColor);
}}
"""


class ThreeBody(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(
            self, size=(600, 600), title="Three-Body Simulation", keys="interactive"
        )
        self.program = gloo.Program(vertex_shader, fragment_shader)
        self.program["position"] = [
            [-1, -1],
            [-1, 1],
            [1, 1],
            [-1, -1],
            [1, 1],
            [1, -1],
        ]
        self.program["iResolution"] = self.size
        self.program["iTime"] = 0.0
        self.program["zoom"] = 1.8
        self.timer = app.Timer("auto", connect=self.on_timer, start=False)
        self.frame_index = 0

    def on_draw(self, event):
        gloo.clear()
        indices = (
            np.arange(self.frame_index - trail_length, self.frame_index) % num_steps
        )
        for i in range(trail_length):
            self.program[f"pointsA[{i}]"] = r1[indices[i]]
            self.program[f"pointsB[{i}]"] = r2[indices[i]]
            self.program[f"pointsC[{i}]"] = r3[indices[i]]
        self.frame_index += 1
        self.program.draw("triangles")

    def on_timer(self, event):
        self.program["iTime"] = event.elapsed
        self.update()

    def save_screenshot(self):
        img = gloo.util._screenshot((0, 0, self.size[0], self.size[1]))
        imsave("capture.png", img)

    def on_key_press(self, event):
        if event.key == "Enter":
            self.save_screenshot()

    def on_resize(self, event):
        self.program["iResolution"] = event.size
        gloo.set_viewport(0, 0, *event.size)

    def run(self):
        self.timer.start()
        self.show(run=True)


if __name__ == "__main__":
    anim = ThreeBody()
    anim.run()
