"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Shader animation of aperiodic rhombus tiling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See the live demo at

    "https://www.shadertoy.com/view/wsKBW1"

:copyright (c) 2020 by Zhao Liang.
"""
import sys

sys.path.append("../glslhelpers")

import argparse
import time

import pyglet

pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key
from shader import Shader


class Escher(pyglet.window.Window):
    def __init__(self, width, height):
        """
        :param width and height: size of the window in pixels.
        :param AA: antialiasing level, AA=4 is good enough (but also slow).
        """
        pyglet.window.Window.__init__(
            self,
            width,
            height,
            caption="Escher impossible tiling",
            resizable=True,
            visible=False,
            vsync=False,
        )
        self._start_time = time.process_time()
        self.shader = Shader(["./glsl/escher.vert"], ["./glsl/escher.frag"])
        self.init_shader()
        self.buffer = pyglet.image.get_buffer_manager().get_color_buffer()

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
            self.shader.uniformf("iTime", time.process_time() - self._start_time)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def on_key_press(self, symbol, modifiers):
        """Keyboard interface.
        """
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def save_screenshot(self):
        self.buffer.save("impossible-tiling.png")

    def run(self, fps=None):
        self.set_visible(True)
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0 / fps)
        pyglet.app.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-size", metavar="s", type=str, default="1200x960", help="window size in pixels"
    )
    args = parser.parse_args()
    w, h = [int(x) for x in args.size.split("x")]
    app = Escher(width=w, height=h)
    app.run()


if __name__ == "__main__":
    main()
