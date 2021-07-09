"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Mobius transformations in hyperbolic 3-space
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code exported and adapted from Roice Nelson's code at

    "https://www.shadertoy.com/view/MstcWr"

References:

    "Visual complex analysis" by Needham.

    "https://www.maths.ox.ac.uk/about-us/departmental-art/dupin-cyclides"

"""
import argparse
import time

import pyglet

pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key

from glslhelpers import Shader


class Mobius(pyglet.window.Window):

    """
    In this animation we show how a Mobius transformation acts on the complex
    plane, the Riemann sphere and the hyperbolic upper half space.

    The "banana" like surface is called Dupin cyclide, which is a cylinder of
    infinite length in the upper half space.

    Keyboard control:
    1. Press 1 to toggle on/off applying the transformation.
    2. Press 2 to toggle on/off applying the hyperbolic scaling.
    3. Press 3 to toggle on/off applying the elliptic rotation.
    4. Press 4 to toggle on/off showing the Riemann sphere.
    5. Press Enter to save screenshot.

    Combinations of the four options give many possible scenes, enjoy!
    """

    def __init__(self, width, height, aa_level):
        pyglet.window.Window.__init__(
            self,
            width,
            height,
            caption="Mobius transformation in hyperbolic 3-space",
            resizable=True,
            visible=False,
            vsync=False,
        )
        self._start_time = time.process_time()
        self.shader = Shader(["./glsl/default.vert"], ["./glsl/mobius/mobius.frag"])
        self.b_apply = True
        self.b_elliptic = True
        self.b_hyperbolic = True
        self.b_riemann = False

        with self.shader:
            self.shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.uniformf("iResolution", width, height, 0.0)
            self.shader.uniformf("iTime", 0.0)
            self.shader.uniformi("b_apply", self.b_apply)
            self.shader.uniformi("b_elliptic", self.b_elliptic)
            self.shader.uniformi("b_hyperbolic", self.b_hyperbolic)
            self.shader.uniformi("b_riemann", self.b_riemann)
            self.shader.uniformi("AA", aa_level)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        with self.shader:
            dt = time.process_time() - self._start_time
            self.shader.uniformf("iTime", dt * 4.)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def on_key_press(self, symbol, modifiers):
        if symbol == key._1:
            self.b_apply = not self.b_apply
            with self.shader:
                self.shader.uniformi("b_apply", self.b_apply)

        if symbol == key._2:
            self.b_hyperbolic = not self.b_hyperbolic
            with self.shader:
                self.shader.uniformi("b_hyperbolic", self.b_hyperbolic)

        if symbol == key._3:
            self.b_elliptic = not self.b_elliptic
            with self.shader:
                self.shader.uniformi("b_elliptic", self.b_elliptic)

        if symbol == key._4:
            self.b_riemann = not self.b_riemann
            with self.shader:
                self.shader.uniformi("b_riemann", self.b_riemann)

        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def save_screenshot(self):
        pyglet.image.get_buffer_manager().get_color_buffer().save("screenshot.png")

    def run(self, fps=None):
        self.set_visible(True)
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0 / fps)
        pyglet.app.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-size", type=str, default="640x360", help="width and height of the window"
    )
    parser.add_argument("-aa", type=int, default=1, help="antialiasing level")

    args = parser.parse_args()

    width, height = [int(i) for i in args.size.split("x")]

    app = Mobius(
        width=width,
        height=height,
        aa_level=args.aa,
    )
    print(app.__doc__)
    app.run(fps=None)
