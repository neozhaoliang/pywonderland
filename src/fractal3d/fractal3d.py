"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make wallpaper raymarching 3D fractals with pygelt and glsl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make wallpapers you should have a decent GPU and change
to a higher antialiasing level (AA) and larger window size.
(e.g. AA=4 and size=1200x960)

Keyboard control:

1. press 'Enter' to save screenshots.
2. press 'Ctrl + S' to load a new scene file.
3. press 'Esc' to escape.

Live demos on shadertoy:

    "apollonian":

        https://www.shadertoy.com/view/WssSWn

    "pseudo Kleinian":

        https://www.shadertoy.com/view/tdfSzM

    "Kleinian Sponge":

        https://www.shadertoy.com/view/3dlXWn

    "debris":

        https://www.shadertoy.com/view/WdsXDH

:copyright (c) 2019 by Zhao Liang.
"""
import sys
sys.path.append("../glslhelpers")

import time
import subprocess
import argparse
import pathlib

import tkinter as tk
from tkinter.filedialog import askopenfilename

import pyglet
pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key

from shader import Shader


def load():
    """Load a scene file in the '/glsl/' folder.
    """
    root = tk.Tk()
    root.withdraw()
    filename = askopenfilename(initialdir="./glsl",
                               initialfile="pseudoKleinian.frag",
                               filetypes=[("Fragment Shader Files", "*.frag")],
                               title="Choose a fragment shader file")
    root.quit()
    return filename


class Fractal3D(pyglet.window.Window):

    def __init__(self, width, height, scene_file, AA=4):
        """
        :param width and height: size of the window in pixels.

        :param scene_file: the fragment shader file to render.

        :param AA: antialiasing level, AA=4 is good enough (but also slow).
        """
        pyglet.window.Window.__init__(self,
                                      width,
                                      height,
                                      caption="Fractal3D",
                                      resizable=True,
                                      visible=False,
                                      vsync=False)
        self._start_time = time.clock()
        self.AA = AA
        self.shader = Shader(["./glsl/fractal3d.vert"], [scene_file])
        self.scene = pathlib.Path(scene_file).resolve().stem
        self.init_shader()
        self.buffer = pyglet.image.get_buffer_manager().get_color_buffer()

    def init_shader(self):
        """Set uniform variables in the shader.
        """
        with self.shader:
            self.shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.uniformf("iResolution", self.width, self.height, 0.0)
            self.shader.uniformf("iTime", 0.0)
            self.shader.uniformi("AA", self.AA)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        with self.shader:
            #self.shader.uniformf("iTime", time.clock() - self._start_time)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def on_key_press(self, symbol, modifiers):
        """Keyboard interface.
        """
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

        if symbol == key.S and (modifiers & key.LCTRL):
            scene_file = load()
            self.shader = Shader(["./glsl/fractal3d.vert"], [scene_file])
            self.init_shader()

    def save_screenshot(self):
        self.buffer.save(self.scene + "-screenshoot.png")

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
                        default="800x480", help="window size in pixels")
    parser.add_argument("-aa", type=int, default=4,
                        help="antialiasing depth")
    parser.add_argument("-file", metavar="f", type=str,
                        default=None, help="scene file name")
    args = parser.parse_args()
    w, h = [int(x) for x in args.size.split("x")]
    scene_file = args.file if args.file is not None else load()
    app = Fractal3D(width=w, height=h, scene_file=scene_file, AA=args.aa)
    app.run()


if __name__ == "__main__":
    main()
