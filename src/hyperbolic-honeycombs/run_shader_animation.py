"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
3D hyperbolic honeycomb animation with pyglet and glsl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reference:

    "http://www.fractalforums.com/general-discussion-b77/solids-many-many-solids/msg43794/#msg43794"

"""
import sys
sys.path.append("../glslhelpers")

import time
import argparse

import pyglet
pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key

from shader import Shader
from texture import create_image_texture


IMG_PATH = "../glslhelpers/textures/rusty_metal.png"


class HyperbolicHoneycomb(pyglet.window.Window):

    def __init__(self, width, height, pqr, AA=2):
        """
        :param width and height: size of the window in pixels.

        :param pqr: Coxeter diagram of the tessellation.

        :param AA: antialiasing level.
        """
        pyglet.window.Window.__init__(self,
                                      width,
                                      height,
                                      caption="Hyperbolic Honeycomb {}-{}-{}".format(*pqr),
                                      resizable=True,
                                      visible=False,
                                      vsync=False)
        self.pqr = pqr
        self._start_time = time.clock()
        self.shader = Shader(["./glsl/hyperbolic3d.vert"], ["./glsl/hyperbolic3d.frag"])
        self.buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        # create the texture
        texture = create_image_texture(IMG_PATH)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

        with self.shader:
            self.shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.uniformf("iResolution", self.width, self.height, 0.0)
            self.shader.uniformf("iTime", 0.0)
            self.shader.uniformi("iTexture", 0)
            self.shader.uniformf("pqr", *self.pqr)
            self.shader.uniformi("AA", AA)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        with self.shader:
            self.shader.uniformf("iTime", time.clock() - self._start_time)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def on_key_press(self, symbol, modifiers):
        """Keyboard interface.
        """
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def save_screenshot(self):
        self.buffer.save("{}-{}-{}-screenshoot.png".format(*self.pqr))

    def run(self, fps=None):
        self.set_visible(True)
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0/fps)
        pyglet.app.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-size", metavar="s", type=str,
                        default="800x600", help="window size in pixels")
    parser.add_argument("-aa", type=int, default=2,
                        help="antialiasing depth")
    parser.add_argument("-pqr", nargs="+", type=int, default=(3, 5, 3),
                        help="Coxeter diagram of the tessellation")
    args = parser.parse_args()
    w, h = [int(x) for x in args.size.split("x")]
    app = HyperbolicHoneycomb(width=w, height=h, pqr=args.pqr, AA=args.aa)
    app.run()


if __name__ == "__main__":
    main()
