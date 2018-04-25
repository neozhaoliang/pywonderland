# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Mobius Transformations of the Hyperbolic 3-Space
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapted from Roice Nelson's code at

    "https://www.shadertoy.com/view/MstcWr"

"""
import time
import subprocess

import pyglet
pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key

from shader import Shader


# windows users need to change this to the path of your ffmpeg executable file.
FFMPEG_EXE = "ffmpeg"


class Mobius(pyglet.window.Window):

    def __init__(self, width, height):
        pyglet.window.Window.__init__(self, width, height, caption="Mobius Transformations",
                                      resizable=True, visible=False, vsync=False)
        self._start_time = time.clock()
        self.shader = Shader(["./glsl/version.txt", "./glsl/mobius.vert"],
                             ["./glsl/version.txt", "./glsl/math.frag",
                              "./glsl/DE.frag", "./glsl/mobius.frag"])
        with self.shader:
            self.shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.vertex_attrib("texcoord", [0, 0, 1, 0, 0, 1, 1, 1])
            self.shader.uniformf("iTime", 0.0)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        with self.shader:
            self.shader.uniformf("iTime", time.clock() - self._start_time)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def run(self, fps=None):
        self.set_visible(True)
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0/fps)
        pyglet.app.run()


if __name__ == "__main__":
    app = Mobius(width=600, height=480)
    app.run(fps=None)
