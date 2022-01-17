"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reaction-Diffusion Simulation with Pyglet and GLSL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make video of the animation you must have `ffmpeg` installed
and can be found on your system path.

For how to use mouse and keyboard to play with the simulation see the doc below.

:copyright (c) 2017 by Zhao Liang.
"""
from __future__ import division

import sys

sys.path.append("../")

import argparse
import re
import subprocess
import time

import numpy as np
import pyglet
from PIL import Image

pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key
from glslhelpers import FrameBuffer, Shader, create_texture_from_ndarray

# windows users need to add the directory that contains
# your "ffmpeg.exe" to the environment variables.
FFMPEG_EXE = "ffmpeg"


# species: [Du, Dv, feed, kill]
ALL_SPECIES = {
    "unstable": [0.210, 0.105, 0.018, 0.051],
    "coral": [0.160, 0.080, 0.060, 0.062],
    "fingerprint": [0.190, 0.050, 0.060, 0.062],
    "bacteria": [0.140, 0.060, 0.035, 0.065],
    "worms": [0.160, 0.080, 0.050, 0.065],
    "zebrafish": [0.160, 0.080, 0.035, 0.060],
    "net": [0.210, 0.105, 0.039, 0.058],
    "worms and loops": [0.210, 0.105, 0.082, 0.060],
    "waves": [0.210, 0.105, 0.014, 0.045],
    "moving spots": [0.210, 0.105, 0.014, 0.054],
    "pulsating solitons": [0.210, 0.105, 0.025, 0.060],
}


def htmlcolors_to_rgba(colors):
    """
    :param colors: a 1d list of 5 html colors of the format "#RRGGBBAA".
        return a 1d list of 20 floats in range [0, 1].
    """
    return [int(x, 16) / 255.0 for s in colors for x in (s[1:3], s[3:5], s[5:7], s[7:])]


def rgba_to_htmlcolors(colors):
    """
    :param colors: a 1d list of length 20 floats in range [0, 1].
        return a 1d list of 5 html colors of the format "#RRGGBBAA".
    """
    hexcolors = [("{:02x}".format(int(255 * x))).upper() for x in colors]
    return ["#{}{}{}{}".format(*hexcolors[4 * i : 4 * i + 4]) for i in range(5)]


def parse(params):
    """
    params: a string of the format "species: color1 ... color5"
        where `species` is the name of the pattern and
        color1-color5 are html colors of the format `#RRGGBBAA`.
        return `species` and a 1d list of 20 floats in range [0, 1].
    """
    species = (params.split(":")[0]).strip()
    colors = re.findall("#[0-9|A-Z]{8}", params)
    return species, htmlcolors_to_rgba(colors)


class GrayScott(pyglet.window.Window):

    """
    ----------------------------------------------------------
    | This simulation uses mouse and keyboard to control the |
    | patterns and colors. At any time you may click or drag |
    | your mouse to draw on the screen.                      |
    |                                                        |
    | Keyboard control:                                      |
    |   1. press "space" to clear the window to blank.       |
    |   2. press "p" to change to a random palette.          |
    |   3. press "s" to change to another species.           |
    |   4. press "Ctrl + s" to save current config.          |
    |   5. press "Ctrl + o" to load a config from the file.  |
    |   6. press "Enter" to take screenshots.                |
    |   7. press "Ctrl + v" to start saving the animation to |
    |      the video and press "Ctrl + v" again to stop.     |
    |   8. press "Esc" to exit.                              |
    ----------------------------------------------------------
    """

    def __init__(
        self,
        width,
        height,
        scale=1.5,
        conf=1,
        mask=None,
        flip=False,
        video=False,
        sample_rate=None,
        video_rate=None,
    ):
        """
        Parameters
        ----------
        :width & height: size of the window in pixels.
        :scale: scaling factor of the texture.
        :conf: line number of the config in the file (`config.txt`).
        :mask: a user-specified image that is used to control the growth of the pattern.
        :flip: flip the white/black pixels in the mask image, only meaningful if there is a mask image.
        :video: whether the video is turned on or off.
        :sample_rate: sample a frame from the animation every these frames.
        :video_rate: frames per second of the video.
        """
        pyglet.window.Window.__init__(
            self,
            width,
            height,
            caption="GrayScott Simulation",
            resizable=True,
            visible=False,
            vsync=False,
        )

        # use two shaders, one for doing the computations and one for rendering to the screen.
        self.reaction_shader = Shader(
            ["./glsl/default.vert"], ["./glsl/grayscott/compute.frag"]
        )
        self.render_shader = Shader(["./glsl/default.vert"], ["./glsl/grayscott/render.frag"])
        self.tex_width, self.tex_height = int(width / scale), int(height / scale)

        try:
            self.species, self.palette = self.load_config(conf)
            print("> Current species: " + self.species + "\n")
        except:
            conf = "unstable: #00000000 #00FF0033 #FFFF0035 #FF000066 #FFFFFF99"
            self.species, self.palette = parse(conf)
            print("> Failed to load the config, using the default one.\n")

        self.species_list = list(ALL_SPECIES.keys())

        # create the uv_texture
        uv_grid = np.zeros((self.tex_height, self.tex_width, 4), dtype=np.float32)
        uv_grid[:, :, 0] = 1.0
        rand_rows = np.random.choice(range(self.tex_height), 5)
        rand_cols = np.random.choice(range(self.tex_width), 5)
        uv_grid[rand_rows, rand_cols, 1] = 1.0
        self.uv_texture = create_texture_from_ndarray(uv_grid)

        # create the mask_texture
        mask_grid = np.ones_like(uv_grid)
        if mask is not None:
            img = (
                Image.open(mask).convert("L").resize((self.tex_width, self.tex_height))
            )
            img = (np.asarray(img) / 255.0).astype(np.float32)
            if flip:
                img = 1.0 - img
            mask_grid[:, :, 0] = img[::-1]
        self.mask_texture = create_texture_from_ndarray(mask_grid)

        # bind the two textures
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(self.uv_texture.target, self.uv_texture.id)
        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(self.mask_texture.target, self.mask_texture.id)

        # use an invisible buffer to do the computations.
        with FrameBuffer() as self.fbo:
            self.fbo.attach_texture(self.uv_texture)

        # we need this because the program samples the position of the mouse in discrete times.
        self.mouse_down = False

        # initialize the two shaders
        with self.reaction_shader:
            self.reaction_shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.reaction_shader.vertex_attrib("texcoord", [0, 0, 1, 0, 0, 1, 1, 1])
            self.reaction_shader.uniformi("iChannel0", 0)
            self.reaction_shader.uniformi("mask_texture", 1)
            self.reaction_shader.uniformf(
                "iResolution", self.tex_width, self.tex_height, 0
            )
            self.reaction_shader.uniformf("iMouse", -1, -1)
            self.reaction_shader.uniformf("params", *ALL_SPECIES[self.species])

        with self.render_shader:
            self.render_shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.render_shader.vertex_attrib("texcoord", [0, 0, 1, 0, 0, 1, 1, 1])
            self.render_shader.uniformi("iChannel0", 0)
            self.render_shader.uniformfv("palette", 5, self.palette)

        self.video_on = video
        self.buffer = pyglet.image.get_buffer_manager().get_color_buffer()

        self.sample_rate = sample_rate
        self.video_rate = video_rate

        self.frame_count = 0

        if video:
            self.ffmpeg_pipe = self.create_new_pipe()

        self.start_time = time.perf_counter()

    def on_draw(self):
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        self.clear()

        if time.perf_counter() - self.start_time > 0.1:
            gl.glViewport(0, 0, self.tex_width, self.tex_height)
            with self.fbo:
                with self.reaction_shader:
                    gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

            gl.glViewport(0, 0, self.width, self.height)
            with self.render_shader:
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
                self.frame_count += 1

        if self.video_on and (self.frame_count % self.sample_rate == 0):
            self.write_video_frame()

    def on_key_press(self, symbol, modifiers):
        """
        Keyboard interface.
        """
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

        if symbol == key.SPACE:
            self.clear_blank_window()

        if symbol == key.P:
            self.use_random_palette()

        if symbol == key.S and not modifiers:
            self.use_next_species()

        if symbol == key.S and (modifiers & key.LCTRL):
            self.save_config()

        if symbol == key.O and (modifiers & key.LCTRL):
            self.require_config_input()

        if symbol == key.V and (modifiers & key.LCTRL):
            self.switch_video()

    def update_species(self, species):
        self.species = species
        with self.reaction_shader:
            self.reaction_shader.uniformf("params", *ALL_SPECIES[species])

    def update_palette(self, palette):
        self.palette = palette
        with self.render_shader:
            self.render_shader.uniformfv("palette", 5, palette)

    def update_mouse(self, x, y):
        with self.fbo:
            with self.reaction_shader:
                self.reaction_shader.uniformf("iMouse", x, y)

    def save_screenshot(self):
        self.buffer.save("screenshot-" + self.species + ".png")

    def save_config(self):
        with open("grayscott_config.txt", "a+") as f:
            f.write(
                self.species + ": " + " ".join(rgba_to_htmlcolors(self.palette)) + "\n"
            )
            print("> Config saved.\n")

    def load_config(self, k):
        with open("grayscott_config.txt", "r") as f:
            for i, line in enumerate(f.readlines()):
                if k == i:
                    return parse(line)
            print("> Config does not exist.\n")

    def require_config_input(self):
        try:
            k = int(input("> Enter the line number in the config file: ").strip())
        except ValueError:
            print("> Invalid input.\n")
            return

        try:
            species, palette = self.load_config(k)
            self.update_species(species)
            self.update_palette(palette)
            print("> Config loaded. Current species: " + self.species)
        except:
            return

    def write_video_frame(self):
        """
        Read frame data from buffer and write it to the video.
        """
        data = self.buffer.get_image_data().get_data("RGBA", -4 * self.width)
        self.ffmpeg_pipe.write(data)

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_down = True
        self.update_mouse(x / self.width, y / self.height)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_down = False
        self.update_mouse(-1, -1)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.mouse_down:
            self.update_mouse(x / self.width, y / self.height)

    def clear_blank_window(self):
        self.update_mouse(-10, -10)

    def use_random_palette(self):
        new_palette = np.random.random(20)
        new_palette[[3, 7, 11, 15, 19]] = sorted(np.random.random(5))
        new_palette[:3] = 0
        self.update_palette(new_palette)

    def use_next_species(self):
        index = self.species_list.index(self.species)
        new_species = self.species_list[(index + 1) % len(self.species_list)]
        self.update_species(new_species)
        print("> Current species: " + self.species + "\n")

    def switch_video(self):
        self.video_on = not self.video_on
        if self.video_on:
            self.ffmpeg_pipe = self.create_new_pipe()
            print("> Writing to video...\n")
        else:
            self.ffmpeg_pipe.close()
            print("> The video is closed.\n")

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
                self.species + ".mp4",
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-size", type=str, default="800x360", help="width and height of the window"
    )
    parser.add_argument(
        "-videorate", type=int, default=24, help="frames per second of the video"
    )
    parser.add_argument(
        "-fps", type=int, default=None, help="frames per second of the animation"
    )
    parser.add_argument(
        "-samplerate",
        type=int,
        default=24,
        help="sample a frame from the animation every these frames",
    )
    parser.add_argument(
        "-scale", type=float, default=1.5, help="level of scaling of the texture"
    )
    parser.add_argument(
        "-conf",
        type=int,
        default=0,
        help="the line number of a config in the configuration file",
    )
    parser.add_argument(
        "-video", action="store_true", help="turn on saving to the video"
    )
    parser.add_argument(
        "-mask",
        type=str,
        default=None,
        help="a mask image to control the growth of the pattern",
    )
    parser.add_argument(
        "-flip",
        type=int,
        default=0,
        help="flip the white/black pixels in the mask image",
    )

    args = parser.parse_args()

    width, height = [int(i) for i in args.size.split("x")]

    app = GrayScott(
        width,
        height,
        scale=args.scale,
        conf=args.conf,
        mask=args.mask,
        flip=args.flip,
        video=args.video,
        sample_rate=args.samplerate,
        video_rate=args.videorate,
    )

    print(app.__doc__)
    app.run(args.fps)
