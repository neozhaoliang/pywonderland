import vispy
from vispy import gloo, app
from vispy.io import imread, imsave

vispy.set_log_level("error")


vertex = """
#version 130

in vec2 position;

void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
}
"""

fragment = """
#version 130

uniform vec3      iResolution;           // viewport resolution (in pixels)
uniform float     iTime;                 // shader playback time (in seconds)
uniform float     iTimeDelta;            // render time (in seconds)
uniform vec4      iMouse;                // mouse pixel coords
uniform vec4      iDate;                 // (year, month, day, time in seconds)
uniform float     iSampleRate;           // sound sample rate (i.e., 44100)
uniform sampler2D iChannel0;             // input channel. XX = 2D/Cube
uniform sampler2D iChannel1;             // input channel. XX = 2D/Cube
uniform sampler2D iChannel2;             // input channel. XX = 2D/Cube
uniform sampler2D iChannel3;             // input channel. XX = 2D/Cube
uniform vec3      iChannelResolution[4]; // channel resolution (in pixels)
uniform float     iChannelTime[4];       // channel playback time (in sec)

out vec4 fragColor;

%s

void main()
{
    mainImage(fragColor, gl_FragCoord.xy);
}
"""

METAL_TEXTURE = "../glslhelpers/textures/rusty_metal.jpg"


class EuclideanHoneycombs(app.Canvas):

    """
    This shader takes a while to compile, please wait!

    ------------------------------------------------------------------
    Keyboard control:

    0. Use mouse drag to rotate the camera.
    1. press 1/2/3/4 to toggle on/off the active mirrors.
    2. press A/B/C to select lattice type.
    3. press s to toggle on/off showing the snub honeycomb.
    4. press d to toggle on/off showing the dual honeycomb.
    5. press Enter to save screenshot.
    6. press Esc to exit.
    ------------------------------------------------------------------
    """

    def __init__(self, size=(800, 480), title="Euclidean honeycombs and their duals",
                 glsl_code="./glsl/euclidean_honeycombs.frag"):
        app.Canvas.__init__(self,
                            keys="interactive",
                            size=size,
                            title=title)

        with open(glsl_code, "r") as f:
            code = f.read()

        self.program = gloo.Program(vertex, fragment % code)
        self.program["position"] = [
            (-1, -1), (-1, 1), (1, 1), (-1, -1), (1, 1), (1, -1)
        ]
        self.program["iTime"] = 0.
        self.program["iResolution"] = (self.physical_size[0], self.physical_size[1], 0)
        self.program["iMouse"] = (0, 0, 0, 0)

        self.T = [1, 1, 1, 0]
        self.latticeType = 0
        self.dual = False
        self.snub = False
        self.program["T"] = self.T
        self.program["latticeType"] = self.latticeType
        self.program["snub"] = self.snub
        self.program["dual"] = self.dual

        img = imread(METAL_TEXTURE)
        tex = gloo.Texture2D(img)
        tex.interpolation = "linear"
        tex.wrapping = "repeat"
        self.program["iChannel0"] = tex
        self.timer = app.Timer('auto', connect=self.on_timer, start=False)

    def on_draw(self, event):
        self.program.draw()

    def on_timer(self, event):
        self.program["iTime"] = event.elapsed
        self.update()

    def on_resize(self, event):
        self.program["iResolution"] = (event.size[0], event.size[1], 0)
        gloo.set_viewport(0, 0, event.size[0], event.size[1])

    def on_mouse_move(self, event):
        if event.is_dragging:
            x, y = event.pos
            px, py = event.press_event.pos
            imouse = (x, self.size[1] - y, px, self.size[1] - py)
            self.program['iMouse'] = imouse

    def save_screenshot(self):
        img = gloo.util._screenshot((0, 0, self.size[0], self.size[1]))
        imsave("capture.png", img)

    def on_key_press(self, event):
        def check():
            if sum(self.T) == 0:
                self.T = [1, 0, 0, 0]

        if event.key == 's':
            self.snub = not self.snub
            self.program['snub'] = self.snub

            if self.snub and self.dual:
                self.dual = False
                self.program['dual'] = self.dual

        if event.key == 'd':
            self.dual = not self.dual
            self.program['dual'] = self.dual

        if event.key == '1':
            self.T[0] = 1 - self.T[0]
            check()
            self.program['T'] = self.T

        if event.key == '2':
            self.T[1] = 1 - self.T[1]
            check()
            self.program['T'] = self.T

        if event.key == '3':
            self.T[2] = 1 - self.T[2]
            check()
            self.program['T'] = self.T

        if event.key == '4':
            self.T[3] = 1 - self.T[3]
            check()
            self.program['T'] = self.T

        if event.key == 'A':
            self.program['latticeType'] = 0

        if event.key == 'B':
            self.program['latticeType'] = 1

        if event.key == 'C':
            self.program['latticeType'] = 2

        if event.key == "Enter":
            self.save_screenshot()

    def run(self):
        self.timer.start()
        self.show(run=True)


if __name__ == "__main__":
    anim = EuclideanHoneycombs()
    print(anim.__doc__)
    anim.run()
