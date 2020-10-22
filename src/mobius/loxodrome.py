# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Loxodromic transformation animation with pyglet and glsl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exported from fb39ca4's shadertoy program at

    https://www.shadertoy.com/view/MsX3D2

"""
import sys

sys.path.append("../glslhelpers")

import argparse
import time

import pyglet

pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key
from pyglet.window import mouse
from shader import Shader
from texture import create_image_texture

WOOD_TEXTURE = "../glslhelpers/textures/wood.jpg"


class MainWindow(pyglet.window.Window):
    def __init__(self, width, height, aa):
        pyglet.window.Window.__init__(
            self,
            width,
            height,
            caption="Loxodromic transformation",
            resizable=True,
            visible=False,
            vsync=False,
        )
        self._start_time = time.clock()
        self.shader = Shader(["./glsl/loxodrome.vert"], ["./glsl/loxodrome.frag"])
        self.buffer = pyglet.image.get_buffer_manager().get_color_buffer()

        texture = create_image_texture(WOOD_TEXTURE)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

        with self.shader:
            self.shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.uniformf("iResolution", width, height, 0.0)
            self.shader.uniformf("iTime", 0.0)
            self.shader.uniformi("iTexture", 0)
            self.shader.uniformi("AA", aa)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        now = time.clock() - self._start_time
        now *= 20
        with self.shader:
            self.shader.uniformf("iTime", now)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def save_screenshot(self):
        self.buffer.save("loxodrome-screenshot.png")

    def on_mouse_press(self, x, y, button, modifiers):
        if button & mouse.LEFT:
            with self.shader:
                self.shader.uniformf("iMouse", x, y, x, y)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button & mouse.LEFT:
            with self.shader:
                x += dx
                y += dy
                x = max(min(x, self.width), 0)
                y = max(min(y, self.height), 0)
                self.shader.uniformf("iMouse", x, y, x, y)

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
        "-size", type=str, default="600x480", help="width and height of the window"
    )
    parser.add_argument("-aa", type=int, default=1, help="antialiasing level")
    args = parser.parse_args()
    width, height = [int(i) for i in args.size.split("x")]
    app = MainWindow(width=width, height=height, aa=args.aa)
    app.run()
