"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Wall paper 3D fractals with pygelt and glsl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import sys
sys.path.append("../glslhelpers")

import time
import subprocess

import pyglet
pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key

from shader import Shader


# more scene files to come
scene_file = "./glsl/pseudokleinian.frag"


class Fractal3D(pyglet.window.Window):

    def __init__(self, width, height):
        pyglet.window.Window.__init__(self,
                                      width,
                                      height,
                                      caption="Fractal3D",
                                      resizable=True,
                                      visible=False,
                                      vsync=False)
        self.set_location(0, 600)
        self._start_time = time.clock()
        self.shader = Shader(["./glsl/fractal3d.vert"], ["./glsl/DE.frag", scene_file])
        with self.shader:
            self.shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.uniformf("iResolution", width, height, 0.0)
            self.shader.uniformf("iTime", 0.0)
            self.shader.uniformi("AA", 4)
 
        self.buffer = pyglet.image.get_buffer_manager().get_color_buffer()

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        with self.shader:
            self.shader.uniformf("iTime", time.clock() - self._start_time)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def save_screenshot(self):
        self.buffer.save("screenshot.png")

    def run(self, fps=None):
        self.set_visible(True)
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0/fps)
        pyglet.app.run()


if __name__ == "__main__":
    app = Fractal3D(1200, 720)
    app.run()
