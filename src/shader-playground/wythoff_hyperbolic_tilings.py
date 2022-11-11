"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Real time animation of hyperbolic tilings with pyglet and glsl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code adapted from Matt Zucker's excellent shadertoy program at

    "https://www.shadertoy.com/view/3tsSzM"

Again Matt's program has lots of rich features and a great UI!

Press "ENTER" to save screenshots and "Esc" to escape.
"""
import sys
sys.path.append("../")

import argparse
import datetime
import time

import pyglet

pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key
from glslhelpers import FrameBuffer, Shader, create_image_texture

FONT_TEXTURE = "../glslhelpers/textures/font.png"
NOISE_TEXTURE = "../glslhelpers/textures/rgba_noise_small.png"


def get_idate():
    now = datetime.datetime.now()
    utcnow = datetime.datetime.utcnow()
    midnight_utc = datetime.datetime.combine(utcnow.date(), datetime.time(0))
    delta = utcnow - midnight_utc
    return (now.year, now.month, now.day, delta.seconds)


class Wythoff(pyglet.window.Window):

    def __init__(self, width, height):
        """
        :param width and height: size of the window in pixels.
        """
        pyglet.window.Window.__init__(
            self,
            width,
            height,
            caption="Wythoff Explorer",
            resizable=True,
            visible=False,
            vsync=False,
        )
        self._start_time = time.perf_counter()
        self._last = self._now = self._start_time
        self._frame_count = 0  # count number of frames rendered so far
        self.shaderA = Shader(
            ["./glsl/default.vert"],
            [
                "./glsl/wythoff_hyperbolic/common.frag",
                "./glsl/wythoff_hyperbolic/BufferA.frag"
            ],
        )

        self.shaderB = Shader(
            ["./glsl/default.vert"],
            [
                "./glsl/wythoff_hyperbolic/common.frag",
                "./glsl/wythoff_hyperbolic/main.frag"
            ],
        )

        self.font_texture = create_image_texture(FONT_TEXTURE)
        self.noise_texture = create_image_texture(NOISE_TEXTURE)
        self.iChannel0 = pyglet.image.Texture.create_for_size(
            gl.GL_TEXTURE_2D, width, height, gl.GL_RGBA32F
        )
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(self.iChannel0.target, self.iChannel0.id)
        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.font_texture)
        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.noise_texture)

        with FrameBuffer() as self.bufferA:
            self.bufferA.attach_texture(self.iChannel0)

        # initialize the shaders
        with self.shaderA:
            self.shaderA.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shaderA.uniformf("iResolution", width, height, 0.0)
            self.shaderA.uniformf("iTime", 0.0)
            self.shaderA.uniformf("iMouse", 0.0, 0.0, 0.0, 0.0)
            self.shaderA.uniformi("iChannel0", 0)
            self.shaderA.uniformi("iChannel1", 1)
            self.shaderA.uniformi("iChannel2", 2)
            self.shaderA.uniformf("iDate", *get_idate())
            self.shaderA.uniformf("iTimeDelta", 0)

        with self.shaderB:
            self.shaderB.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shaderB.uniformf("iResolution", width, height, 0.0)
            self.shaderB.uniformf("iTime", 0.0)
            self.shaderB.uniformf("iMouse", 0.0, 0.0, 0.0, 0.0)
            self.shaderB.uniformi("iChannel0", 0)
            self.shaderB.uniformi("iChannel1", 1)
            self.shaderB.uniformi("iChannel2", 2)
            self.shaderB.uniformf("iDate", *get_idate())
            self.shaderA.uniformf("iTimeDelta", 0)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        self._last = self._now
        self._now = time.perf_counter()
        itime = self._now - self._start_time
        idate = get_idate()
        delta = self._now - self._last
        with self.bufferA:
            with self.shaderA:
                self.shaderA.uniformf("iTime", itime)
                self.shaderA.uniformf("iDate", *idate)
                self.shaderA.uniformf("iTimeDelta", delta)
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        with self.shaderB:
            self.shaderB.uniformf("iTime", itime)
            self.shaderB.uniformf("iDate", *idate)
            self.shaderB.uniformf("iTimeDelta", delta)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        self._frame_count += 1

    def on_key_press(self, symbol, modifiers):
        """Keyboard interface.
        """
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def on_mouse_press(self, x, y, button, modifiers):
        if button & pyglet.window.mouse.LEFT:
            with self.shaderA:
                self.shaderA.uniformf("iMouse", x, y, x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        """Don't forget reset 'iMouse' when mouse is released.
        """
        with self.shaderA:
            self.shaderA.uniformf("iMouse", 0, 0, 0, 0)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button & pyglet.window.mouse.LEFT:
            with self.shaderA:
                x += dx
                y += dy
                x = max(min(x, self.width), 0)
                y = max(min(y, self.height), 0)
                self.shaderA.uniformf("iMouse", x, y, x, y)

    def save_screenshot(self):
        image_buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        image_buffer.save("screenshoot.png")

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
        "-size", metavar="s", type=str, default="800x480",
        help="window size in pixels"
    )
    args = parser.parse_args()
    w, h = [int(x) for x in args.size.split("x")]
    app = Wythoff(width=w, height=h)
    app.run()


if __name__ == "__main__":
    main()
