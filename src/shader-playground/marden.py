"""
~~~~~~~~~~~~~~~~
Marden's theorem
~~~~~~~~~~~~~~~~

This animation shows a beautiful connection between electrostatics,
complex analysis and geometry.

See

    "https://en.wikipedia.org/wiki/Marden%27s_theorem"

and John Baez's nice explanation

    "https://johncarlosbaez.wordpress.com/2021/05/24/electrostatics-and-the-gauss-lucas-theorem/"
"""
import argparse
import time

import pyglet

pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key

from glslhelpers import Shader


class Marden(pyglet.window.Window):

    def __init__(self, width, height):
        """
        :param width and height: size of the window in pixels.
        """
        pyglet.window.Window.__init__(
            self,
            width,
            height,
            caption="Marden's theorem",
            resizable=True,
            visible=False,
            vsync=False,
        )
        self._start_time = time.process_time()
        self.shader = Shader(["./glsl/default.vert"],
                             ["./glsl/marden/marden.frag"])
        self.init_shader()
        self.set_visible(True)

    def init_shader(self):
        """Set uniform variables in the shader.
        """
        with self.shader:
            self.shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.uniformf("iResolution", self.width, self.height, 0.0)
            self.shader.uniformf("iTime", 0.0)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)

        with self.shader:
            dt = time.process_time() - self._start_time
            self.shader.uniformf("iTime", dt)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def on_key_press(self, symbol, modifiers):
        """Keyboard interface.
        """
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def save_screenshot(self):
        pyglet.image.get_buffer_manager().get_color_buffer().save("marden.png")

    def run(self, fps=None):
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0 / fps)
        pyglet.app.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-size", metavar="s", type=str, default="800x450", help="window size in pixels"
    )
    args = parser.parse_args()
    w, h = [int(x) for x in args.size.split("x")]
    app = Marden(width=w, height=h)
    app.run()


if __name__ == "__main__":
    main()
