# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reaction-Diffusion Simulation with Pyglet and GLSL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage: python main.py

For how to use mouse and keyboard to play with the simulation see the doc below.

:copyright (c) 2017 by Zhao Liang.
"""

import json
import numpy as np

try:
    raw_input
except NameError:
    raw_input = input

import pyglet
pyglet.options['debug_gl'] = False
import pyglet.gl as gl

from shader import Shader
from framebuffer import FrameBuffer


# pattern: [rU, rV, feed, kill]
SPECIES = {'bacteria1':       [0.16, 0.08, 0.035, 0.065],
           'bacteria2':       [0.14, 0.06, 0.035, 0.065],
           'coral':           [0.16, 0.08, 0.060, 0.062],
           'fingerprint':     [0.19, 0.05, 0.060, 0.062],
           'spirals':         [0.10, 0.10, 0.018, 0.050],
           'spirals_dense':   [0.12, 0.08, 0.020, 0.050],
           'spirals_fast':    [0.10, 0.16, 0.020, 0.050],
           'unstable':        [0.16, 0.08, 0.020, 0.055],
           'worms1':          [0.16, 0.08, 0.050, 0.065],
           'worms2':          [0.16, 0.08, 0.054, 0.063],
           'zebrafish':       [0.16, 0.08, 0.035, 0.060],}

DEFAULT_PATTERN = 'unstable'
DEFAULT_PALETTE = np.array([(0.0, 0.0, 0.0, 0.0),
                            (0.0, 1.0, 0.0, 0.2),
                            (1.0, 1.0, 0.0, 0.21),
                            (1.0, 0.0, 0.0, 0.4),
                            (1.0, 1.0, 1.0, 0.6)])


def create_uv_texture(width, height):
    """Create a pyglet texture instance from a numpy ndarray."""
    uv_grid = np.zeros((height, width, 4), dtype=np.float32)
    uv_grid[:, :, 0] = 1.0
    uv_grid[height//2, width//2, 1] = 1.0
    texture = pyglet.image.Texture.create_for_size(gl.GL_TEXTURE_2D, width, height, gl.GL_RGBA32F_ARB)
    gl.glBindTexture(texture.target, texture.id)
    gl.glTexImage2D(texture.target, texture.level, gl.GL_RGBA32F_ARB,
                    width, height, 0, gl.GL_RGBA, gl.GL_FLOAT, uv_grid.ctypes.data)
    gl.glBindTexture(texture.target, 0)
    return texture


class GrayScott(pyglet.window.Window):
    """
    ----------------------------------------------------------
    | This simulation uses mouse and keyboard to control the |
    | patterns and colors. At any time you may click or drag |
    | your mouse to draw on the screen.                      |
    |                                                        |
    | Keyboad control:                                       |
    |   1. press 'space' to clear the window to blank.       |
    |   2. press 'p' to change to a random palette.          |
    |   3. press 's' to change to another pattern.           |
    |   4. press 'Ctrl + r' to reset to default.             |
    |   5. press 'Ctrl + s' to save current config.          |
    |   6. press 'Ctrl + o' to load config from json file.   |
    |   7. press 'Enter' to take screenshots.                |
    |   8. press 'Esc' to exit.                              |
    ----------------------------------------------------------
    """

    def __init__(self, width, height, scale=2):
        """
        width, height:
            size of the window in pixels.
        scale:
            the size of the texture is (width//scale) x (height//scale).
        """
        pyglet.window.Window.__init__(self, width, height, caption='GrayScott Simulation',
                                      visible=False, vsync=False)
        self.reaction_shader = Shader('./glsl/default.vert', './glsl/reaction.frag')
        self.render_shader = Shader('./glsl/default.vert', './glsl/render.frag')
        self.pattern = DEFAULT_PATTERN
        self.palette = DEFAULT_PALETTE
        self.tex_width = width // scale
        self.tex_height = height // scale
        self.uv_texture = create_uv_texture(width//scale, height//scale)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(self.uv_texture.target, self.uv_texture.id)

        # use an invisible buffer to do the computation.
        with FrameBuffer() as self.fbo:
            self.fbo.attach_texture(self.uv_texture)

        # why do we need this? the reason is in the 'on_mouse_drag' function.
        self.mouse_down = False

        # put all patterns in a list for iterating over them.
        self._species = list(SPECIES.keys())

        # set the uniforms and attributes in the two shaders.
        self.init_reaction_shader()
        self.init_render_shader()

    def set_viewport(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, 1, 0, 1, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()

        # since we are rendering to the invisible framebuffer,
        # the size is the texture's size.
        self.set_viewport(self.tex_width, self.tex_height)
        with self.fbo:
            with self.reaction_shader:
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        # now we render to the actual window, hence the size is window's size.
        self.set_viewport(self.width, self.height)
        with self.render_shader:
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def use_pattern(self, pattern):
        self.pattern = pattern
        rU, rV, feed, kill = SPECIES[pattern]
        with self.reaction_shader:
            self.reaction_shader.set_uniformf('feed', feed)
            self.reaction_shader.set_uniformf('kill', kill)
            self.reaction_shader.set_uniformf('rU', rU)
            self.reaction_shader.set_uniformf('rV', rV)

    def use_palette(self, palette):
        self.palette = palette
        color1, color2, color3, color4, color5 = palette
        with self.render_shader:
            self.render_shader.set_uniformf('color1', *color1)
            self.render_shader.set_uniformf('color2', *color2)
            self.render_shader.set_uniformf('color3', *color3)
            self.render_shader.set_uniformf('color4', *color4)
            self.render_shader.set_uniformf('color5', *color5)

    def init_reaction_shader(self):
        with self.reaction_shader:
            self.reaction_shader.set_uniformi('uv_texture', 0)
            self.reaction_shader.set_uniformf('dx', 1.0/self.tex_width)
            self.reaction_shader.set_uniformf('dy', 1.0/self.tex_height)
            # the order of the vertices and texcoords matters,
            # since we will call 'GL_TRIANGLE_STRIP' to draw them.
            self.reaction_shader.set_vertex_attrib('position', [-1, -1, 1, -1, -1, 1, 1, 1])
            self.reaction_shader.set_vertex_attrib('texcoord', [0, 0, 1, 0, 0, 1, 1, 1])
            self.reaction_shader.set_uniformf('u_mouse', -1, -1)
        self.use_pattern(self.pattern)

    def init_render_shader(self):
        with self.render_shader:
            self.render_shader.set_uniformi('uv_texture', 0)
            self.render_shader.set_vertex_attrib('position', [-1, -1, 1, -1, -1, 1, 1, 1])
            self.render_shader.set_vertex_attrib('texcoord', [0, 0, 1, 0, 0, 1, 1, 1])
        self.use_palette(self.palette)

    def update_mouse(self, *u_mouse):
        self.set_viewport(self.tex_width, self.tex_height)
        with self.fbo:
            with self.reaction_shader:
                self.reaction_shader.set_uniformf('u_mouse', *u_mouse)

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_down = True
        bx = x / float(self.width)
        by = y / float(self.height)
        self.update_mouse(bx, by)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_down = False
        self.update_mouse(-1, -1)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.mouse_down:
            bx = x / float(self.width)
            by = y / float(self.height)
            self.update_mouse(bx, by)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            self.save_screenshot()

        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()

        # clear to blank window
        if symbol == pyglet.window.key.SPACE:
            self.update_mouse(-10, -10)

        if symbol == pyglet.window.key.S:
            if modifiers != pyglet.window.key.LCTRL:
                self.change_pattern()

        if symbol == pyglet.window.key.P:
            self.change_palette()

        if symbol == pyglet.window.key.R:
            if modifiers & pyglet.window.key.LCTRL:
                self.restore_default()

        if symbol == pyglet.window.key.S:
            if modifiers & pyglet.window.key.LCTRL:
                self.save_config()

        if symbol == pyglet.window.key.O:
            if modifiers & pyglet.window.key.LCTRL:
                self.load_config()

    def save_screenshot(self):
        index = np.random.randint(0, 1000)
        img = pyglet.image.get_buffer_manager().get_color_buffer()
        img.save('screenshot{:03d}.png'.format(index))

    def restore_default(self):
        self.use_palette(DEFAULT_PALETTE)
        self.use_pattern(DEFAULT_PATTERN)
        print('> Using default config.\n')

    def save_config(self):
        """Save current config to the json file."""
        with open('palette.json', 'a+') as f:
            data = json.dumps({self.pattern: self.palette.tolist()})
            f.write(data + '\n')
            print('> Config saved.\n')

    def load_config(self):
        """Load a config from the json file."""
        try:
            num = int(raw_input('> Enter the line number in json file: ').strip())
        except ValueError:
            print('> Invalid input.\n')
            return

        with open('palette.json', 'r') as f:
            lines = f.readlines()
            if 1 <= num <= len(lines):
                (pattern, palette), = json.loads(lines[num - 1]).items()
                self.use_pattern(pattern)
                self.use_palette(palette)
                print('> Config loaded. Current config: ' + self.pattern + '. Draw on it!\n')
            else:
                print('> Config does not exist in json file.\n')

    def change_palette(self):
        """Use a random palette."""
        alphas = sorted(np.random.random(5))
        palette = np.random.random((5, 4))
        # the first row is set to 0 to make the background black.
        palette[0] = 0.0
        palette[:, -1] = alphas
        palette = palette.round(3)
        self.use_palette(palette)
        print('> Current palette: ')
        print(palette)
        print('\n')

    def change_pattern(self):
        """Use the next pattern in the list `self._species`."""
        index = self._species.index(self.pattern)
        next_pattern = self._species[(index + 1) % len(self._species)]
        self.use_pattern(next_pattern)
        print('> Current pattern: ' + self.pattern
              + '. If the screen is blank, draw on it!\n')

    def run(self, fps=None):
        """fps: frames per second."""
        self.set_visible(True)
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0/fps)
        pyglet.app.run()


if __name__ == '__main__':
    app = GrayScott(width=600, height=480, scale=2)
    print(app.__doc__)
    app.run(fps=300)
