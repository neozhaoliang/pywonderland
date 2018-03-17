# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A Manderbrot Set Example with Pyglet and GLSL 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright (c) 2017 by Zhao Liang.
"""
import numpy as np

import pyglet
pyglet.options['debug_gl'] = False
import pyglet.gl as gl
from shader import Shader


class Mandelbrot(pyglet.window.Window):

    def __init__(self, width, height):

        pyglet.window.Window.__init__(self, width, height, caption="Manderbrot Set",
                                      resizable=True, visible=False, vsync=False)
        self.shader = Shader(['./glsl/mandel.vert'], ['./glsl/mandel.frag'])
        with self.shader:
            self.shader.vertex_attrib('position', [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.vertex_attrib('texcoord', [0, 0, 1, 0, 0, 1, 1, 1])
            
    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        with self.shader:
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
            
    def run(self, fps=None):
        self.set_visible(True)
        pyglet.app.run()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            img = pyglet.image.get_buffer_manager().get_color_buffer()
            img.save("mandelbrot.png")

if __name__ == '__main__':
    app = Mandelbrot(width=800, height=640)
    app.run(fps=None)
