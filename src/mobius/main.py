# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Mobius Transformations of the Hyperbolic 3-Space
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code exported and adapted from Roice Nelson's code at

    "https://www.shadertoy.com/view/MstcWr"

Reference:

    "Visual complex analysis" by Needham.

"""
import time
import subprocess

import pyglet
pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key

from shader import Shader


# windows users need to add the directory that contains
# your "ffmpeg.exe" to the environment variables.
FFMPEG_EXE = "ffmpeg"


class Mobius(pyglet.window.Window):
    """
    Keyboard control:
    1. Press 1 to toggle on/off applying the transformation.
    2. Press 2 to toggle on/off applying the hyperbolic scaling.
    3. Press 3 to toggle on/off applying the elliptic rotation.
    4. Press Ctrl + v to toggle on/off saving the video.
    5. Press Enter to save screenshot.
    """
    def __init__(self, width, height, sample_rate=8,
                 video_rate=24, antialiasing=1):
        pyglet.window.Window.__init__(self,
                                      width,
                                      height,
                                      caption="Mobius transformation in hyperbolic 3-space",
                                      resizable=True,
                                      visible=False,
                                      vsync=False)
        self._start_time = time.clock()
        self.shader = Shader(["./glsl/mobius.vert"], ["./glsl/helpers.frag", "./glsl/mobius.frag"])
        self.apply = True
        self.elliptic = True
        self.hyperbolic = True
        self.video_on = False
        self.buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        self.sample_rate = sample_rate
        self.video_rate = video_rate
        self.frame_count = 0

        with self.shader:
            self.shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.uniformf("iResolution", width, height, 0.0)
            self.shader.uniformf("iTime", 0.0)
            self.shader.uniformi("iApply", self.apply)
            self.shader.uniformi("iElliptic", self.elliptic)
            self.shader.uniformi("iHyperbolic", self.hyperbolic)
            self.shader.uniformf("iMobius.A", -1, 0.0)
            self.shader.uniformf("iMobius.B", 1, 0.0)
            self.shader.uniformf("iMobius.C", -1, 0.0)
            self.shader.uniformf("iMobius.D", -1, 0.0)
            self.shader.uniformi("AA", antialiasing)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        with self.shader:
            self.shader.uniformf("iTime", time.clock() - self._start_time)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        if self.video_on and (self.frame_count % self.sample_rate == 0):
            self.write_video_frame()

        self.frame_count += 1

    def on_key_press(self, symbol, modifiers):
        if symbol == key._1:
            self.apply = not self.apply
            with self.shader:
                self.shader.uniformi("iApply", self.apply)

        if symbol == key._2:
            self.hyperbolic = not self.hyperbolic
            with self.shader:
                self.shader.uniformi("iHyperbolic", self.hyperbolic)

        if symbol == key._3:
            self.elliptic = not self.elliptic
            with self.shader:
                self.shader.uniformi("iElliptic", self.elliptic)

        if symbol == key.V and (modifiers & key.LCTRL):
            self.switch_video()

        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def scene_info(self):
        parabolic = not (self.elliptic or self.hyperbolic)
        loxodromic = self.elliptic and self.hyperbolic
        info = ""
        if parabolic:
            if self.apply:
                info += "parabolic-translation-horosphere"
            else:
                info += "parabolic-translation-horoplane"
        elif loxodromic:
            if self.apply:
                info += "loxodromic-Dupin-cyclide"
            else:
                info += "loxodromic-cone"
        elif self.elliptic:
            if self.apply:
                info += "elliptic-roatation-Dupin-cyclide"
            else:
                info += "elliptic-rotation-cone"
        else:
            if self.apply:
                info += "hyperbolic-scaling-Dupin-cyclide"
            else:
                info += "hyperbolic-scaling-cone"
        return info

    def save_screenshot(self):
        self.buffer.save(self.scene_info() + ".png")

    def switch_video(self):
        self.video_on = not self.video_on
        if self.video_on:
            self.ffmpeg_pipe = self.create_new_pipe()
            print("> Writing to video...\n")
        else:
            self.ffmpeg_pipe.close()
            print("> The video is closed.\n")

    def write_video_frame(self):
        data = self.buffer.get_image_data().get_data("RGBA", -4 * self.width)
        self.ffmpeg_pipe.write(data)

    def create_new_pipe(self):
        ffmpeg = subprocess.Popen((FFMPEG_EXE,
                                   "-threads", "0",
                                   "-loglevel", "panic",
                                   "-r", "%d" % self.video_rate,
                                   "-f", "rawvideo",
                                   "-pix_fmt", "rgba",
                                   "-s", "%dx%d" % (self.width, self.height),
                                   "-i", "-",
                                   "-c:v", "libx264",
                                   "-crf", "20",
                                   "-y", self.scene_info() + ".mp4"
                                  ), stdin=subprocess.PIPE)
        return ffmpeg.stdin

    def run(self, fps=None):
        self.set_visible(True)
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0/fps)
        pyglet.app.run()


if __name__ == "__main__":
    app = Mobius(width=640, height=480, sample_rate=8,
                 video_rate=24, antialiasing=1)
    print(app.__doc__)
    app.run(fps=None)
