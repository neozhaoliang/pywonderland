"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Shader animation of Wythoff construction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exported from Matt Zucker's excellent shadertoy program at

    "https://www.shadertoy.com/view/Md3yRB"
"""
import sys
sys.path.append("../")

import os
import argparse
import subprocess
import time

import pyglet

pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key
from glslhelpers import FrameBuffer, Shader, create_image_texture


FFMPEG_EXE = "ffmpeg"
FONT_TEXTURE = "../glslhelpers/textures/font.png"
GLSL_DIR = os.path.join(os.getcwd(), "glsl/wythoff")


class Wythoff(pyglet.window.Window):

    """
    User interface:
      1. use mouse click to play with the ui.
      2. press `Enter` to save screenshots.
      3. press `Ctrl+v` to start saving video and `Ctrl+v` again to stop.
      4. press `Esc` to exit.
    """

    def __init__(self, width, height, aa=1, video_rate=16, sample_rate=4):
        """
        :param width and height: size of the window in pixels.

        :param aa: antialiasing level, a higher value will give better
            result but also slow down the animation. (aa=2 is recommended)
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
        self.video_rate = video_rate
        self.video_on = False
        self.sample_rate = sample_rate
        self._start_time = time.perf_counter()
        self._frame_count = 0  # count number of frames rendered so far
        self.aa = aa
        # shader A draws the UI
        self.shaderA = Shader(
            [os.path.join(GLSL_DIR, "wythoff.vert")],
            [os.path.join(GLSL_DIR, "common.frag"),
             os.path.join(GLSL_DIR, "BufferA.frag")])
        # shadwr B draws the polyhedra
        self.shaderB = Shader(
            [os.path.join(GLSL_DIR, "wythoff.vert")],
            [os.path.join(GLSL_DIR, "common.frag"),
             os.path.join(GLSL_DIR, "BufferB.frag")])
        # shader C puts them together
        self.shaderC = Shader(
            [os.path.join(GLSL_DIR, "wythoff.vert")],
            [os.path.join(GLSL_DIR, "common.frag"),
             os.path.join(GLSL_DIR, "main.frag")])
        self.font_texture = create_image_texture(FONT_TEXTURE)
        self.iChannel0 = pyglet.image.Texture.create_for_size(
            gl.GL_TEXTURE_2D, width, height, gl.GL_RGBA32F
        )
        self.iChannel1 = pyglet.image.Texture.create_for_size(
            gl.GL_TEXTURE_2D, width, height, gl.GL_RGBA32F
        )
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(self.iChannel0.target, self.iChannel0.id)
        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(self.iChannel1.target, self.iChannel1.id)
        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.font_texture)

        # frame buffer A renders the UI to texture iChannel0
        with FrameBuffer() as self.bufferA:
            self.bufferA.attach_texture(self.iChannel0)
        # frame buffer B render the polyhedra to texture iChannel1
        with FrameBuffer() as self.bufferB:
            self.bufferB.attach_texture(self.iChannel1)

        # initialize the shaders

        with self.shaderA:
            self.shaderA.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shaderA.uniformf("iResolution", width, height, 0.0)
            self.shaderA.uniformf("iTime", 0.0)
            self.shaderA.uniformf("iMouse", 0.0, 0.0, 0.0, 0.0)
            self.shaderA.uniformi("iChannel0", 0)
            self.shaderA.uniformi("iFrame", 0)

        with self.shaderB:
            self.shaderB.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shaderB.uniformf("iResolution", width, height, 0.0)
            self.shaderB.uniformf("iTime", 0.0)
            self.shaderB.uniformf("iMouse", 0.0, 0.0, 0.0, 0.0)
            self.shaderB.uniformi("iChannel0", 0)
            self.shaderB.uniformi("AA", self.aa)

        with self.shaderC:
            self.shaderC.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shaderC.uniformf("iResolution", width, height, 0.0)
            self.shaderC.uniformf("iTime", 0.0)
            self.shaderC.uniformf("iMouse", 0.0, 0.0, 0.0, 0.0)
            self.shaderC.uniformi("iChannel0", 0)
            self.shaderC.uniformi("iChannel1", 1)
            self.shaderC.uniformi("iTexture", 2)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        now = time.perf_counter() - self._start_time
        with self.bufferA:
            with self.shaderA:
                self.shaderA.uniformf("iTime", now)
                self.shaderA.uniformi("iFrame", self._frame_count)
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        with self.bufferB:
            with self.shaderB:
                self.shaderB.uniformf("iTime", now)
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        with self.shaderC:
            self.shaderC.uniformf("iTime", now)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        if self.video_on and (self._frame_count % self.sample_rate == 0):
            self.write_video_frame()

        self._frame_count += 1

    def on_key_press(self, symbol, modifiers):
        """Keyboard interface.
        """
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

        if symbol == key.V and (modifiers & key.LCTRL):
            self.switch_video()

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
        image_buffer.save("screenshot.png")

    def switch_video(self):
        self.video_on = not self.video_on
        if self.video_on:
            self.ffmpeg_pipe = self.create_new_pipe()
            print("> Writing to video...\n")
        else:
            self.ffmpeg_pipe.close()
            print("> The video is closed.\n")

    def write_video_frame(self):
        data = (
            pyglet.image.get_buffer_manager()
            .get_color_buffer()
            .get_image_data()
            .get_data("RGBA", -4 * self.width)
        )
        self.ffmpeg_pipe.write(data)

    def create_new_pipe(self):
        ffmpeg = subprocess.Popen(
            (
                FFMPEG_EXE,
                "-threads",
                "0",
                "-loglevel",
                "panic",
                "-r",
                "%d" % self.video_rate,
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgba",
                "-s",
                "%dx%d" % (self.width, self.height),
                "-i",
                "-",
                "-c:v",
                "libx264",
                "-crf",
                "20",
                "-y",
                "test.mp4",
            ),
            stdin=subprocess.PIPE,
        )
        return ffmpeg.stdin

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
    parser.add_argument(
        "-aa", type=int, default=2, help="antialiasing level"
    )
    parser.add_argument(
        "-video_rate", type=int, default=16, help="fps of the video"
    )
    parser.add_argument(
        "-sample_rate",
        type=int,
        default=4,
        help="how often a frame is sampled and ouput to video",
    )
    args = parser.parse_args()
    w, h = [int(x) for x in args.size.split("x")]
    app = Wythoff(
        width=w,
        height=h,
        aa=args.aa,
        video_rate=args.video_rate,
        sample_rate=args.sample_rate,
    )
    print(app.__doc__)
    app.run()


if __name__ == "__main__":
    main()
