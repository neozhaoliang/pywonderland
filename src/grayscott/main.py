# pylint: disable=unused-argument
# pylint: disable=redefined-builtin

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reaction-Diffusion Simulation with Pyglet and GLSL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage: python main.py

For how to use mouse and keyboard to play with the simulation see the doc below.

:copyright (c) 2017 by Zhao Liang.
"""

import os, shutil

if os.path.exists('frames'):
    shutil.rmtree('frames')
os.makedirs('frames')

import json
import numpy as np

try:
    raw_input
except NameError:
    raw_input = input

import pyglet
pyglet.options['debug_gl'] = False
import pyglet.gl as gl

from PIL import Image
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
           'unstable':        [0.2097, 0.105, 0.018, 0.051],
           'net':             [0.2097, 0.105, 0.039, 0.058],
           'worms1':          [0.16, 0.08, 0.050, 0.065],
           'worms2':          [0.16, 0.08, 0.054, 0.063],
           'zebrafish':       [0.16, 0.08, 0.035, 0.060],}


def create_texture_from_array(array):
    """Create a pyglet texture instance from a numpy ndarray."""
    height, width = array.shape[:2]
    texture = pyglet.image.Texture.create_for_size(gl.GL_TEXTURE_2D, width, height, gl.GL_RGBA32F_ARB)
    gl.glBindTexture(texture.target, texture.id)
    gl.glTexImage2D(texture.target, texture.level, gl.GL_RGBA32F_ARB,
                    width, height, 0, gl.GL_RGBA, gl.GL_FLOAT, array.ctypes.data)
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
    |   4. press 'Ctrl + s' to save current config.          |
    |   5. press 'Ctrl + o' to load config from json file.   |
    |   6. press 'Enter' to take screenshots.                |
    |   7. press 'Ctrl + v' to start saving frames and press |
    |      'Ctrl + v' again to stop saving frames.           |
    |   8. press 'Esc' to exit.                              |
    ----------------------------------------------------------
    """
    
    def __init__(self, width, height, scale, config, video=False, mask=None, flip=False):
        """
        width, height: size of the window in pixels.
        scale: the size of the texture is (width//scale) x (height//scale).
        config: a line number in the file `config.json`.
        video: whether or not saving frams from the beginning.
        mask: a user-defined image that will be converted to a white and black mask image.
        filp: choose whether the black pixels or the white pixels in the mask image are shown.
        """
        pyglet.window.Window.__init__(self, width, height, caption='GrayScott Simulation',
                                      visible=False, vsync=False)
        self.tex_width, self.tex_height = width // scale, height // scale
        self.load_config(config)
        
        # Choose which reaction shader to use according to whether there is a mask image.
        if mask is None:
            self.reaction_shader = Shader('./glsl/default.vert', './glsl/reaction.frag')       
            self.feed_texture = None
        else:
            self.reaction_shader = Shader('./glsl/default.vert', './glsl/reaction_with_mask.frag')
            img = Image.open(mask).convert('L').resize((self.tex_width, self.tex_height))
            img = (np.asarray(img) / 255.0).astype(np.float32)
            feed_texture = np.zeros(img.shape+(4,), dtype=np.float32)
            if flip:
                img = img[::-1]
            else:
                img = 1 - img[::-1]
            feed_texture[:, :, 0] = img * SPECIES[self.pattern][2]
            self.feed_texture = create_texture_from_array(feed_texture)
            
        self.render_shader = Shader('./glsl/default.vert', './glsl/render.frag')
        
        # Genetate the uv_texture
        uv_grid = np.zeros((self.tex_height, self.tex_width, 4), dtype=np.float32)
        uv_grid[:, :, 0] = 1.0

        if self.feed_texture is None:
            # start evovling from the center.
            uv_grid[self.tex_height//2, self.tex_width//2, 1] = 1.0
        else:
            # start evovling from 10 random points.
            rand_rows = np.random.choice(range(self.tex_height), 10)
            rand_cols = np.random.choice(range(self.tex_width), 10)
            uv_grid[rand_rows, rand_cols, 1] = 1.0
        self.uv_texture = create_texture_from_array(uv_grid)
        
        # Bind the (one or two) texture(s).
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(self.uv_texture.target, self.uv_texture.id)
        if self.feed_texture is not None:
            gl.glActiveTexture(gl.GL_TEXTURE1)
            gl.glBindTexture(self.feed_texture.target, self.feed_texture.id)
            
        # Use an invisible buffer to do the computation.
        with FrameBuffer() as self.fbo:
            self.fbo.attach_texture(self.uv_texture)

        self.mouse_down = False
        self._species_names = list(SPECIES.keys())

        # The next four attributes are used for saving frames.
        self.frame_count = 0
        self.video_on = video
        self.skip = 100
        self.max_frames = 100000

        # Finally initialize the two shaders.
        self.init_reaction_shader()
        self.init_render_shader()

      
    def load_config(self, config=None):
        """Load a config from the json file."""
        if config is None:
            try:
                config = int(raw_input('> Enter the line number in json file: ').strip())
            except ValueError:
                print('> Invalid input.\n')
                return

        with open('config.json', 'r') as f:
            lines = f.readlines()
            if 1 <= config <= len(lines):
                (pattern, palette), = json.loads(lines[config - 1]).items()
                self.pattern = pattern
                self.palette = palette
                print('> Config loaded. Current config: ' + self.pattern + '. Draw on it!\n')
            else:
                print('> Config does not exist in json file.\n')
                
                
    def init_reaction_shader(self):
        with self.reaction_shader:
            self.reaction_shader.set_uniformi('uv_texture', 0)
            if self.feed_texture is not None:
                self.reaction_shader.set_uniformi('feed_texture', 1)
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
            
            
    def use_pattern(self, pattern):
        rU, rV, feed, kill = SPECIES[pattern]
        with self.reaction_shader:
            self.reaction_shader.set_uniformf('kill', kill)
            self.reaction_shader.set_uniformf('rU', rU)
            self.reaction_shader.set_uniformf('rV', rV)
            if self.feed_texture is None:
                self.reaction_shader.set_uniformf('feed', feed)
                
                
    def use_palette(self, palette):
        color1, color2, color3, color4, color5 = palette
        with self.render_shader:
            self.render_shader.set_uniformf('color1', *color1)
            self.render_shader.set_uniformf('color2', *color2)
            self.render_shader.set_uniformf('color3', *color3)
            self.render_shader.set_uniformf('color4', *color4)
            self.render_shader.set_uniformf('color5', *color5)
            
      
    def set_viewport(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, 1, 0, 1, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        
    
    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()

        # Since we are rendering to the invisible framebuffer,
        # the size is the texture's size.
        self.set_viewport(self.tex_width, self.tex_height)

        with self.fbo:
            with self.reaction_shader:
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        # Now we render to the actual window, hence the size is window's size.
        self.set_viewport(self.width, self.height)
        with self.render_shader:
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
            
        if self.video_on:
            if (self.frame_count % self.skip == 0) and (self.frame_count < self.max_frames):
                self.save_video_frame(self.frame_count // self.skip)

        self.frame_count += 1
        
        
    def save_video_frame(self, index):
        img = pyglet.image.get_buffer_manager().get_color_buffer()
        img.save(os.path.join('frames', 'frame{:05d}.png'.format(index)))
        
        
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
            
        if symbol == pyglet.window.key.S and not modifiers:
            self.change_pattern()

        if symbol == pyglet.window.key.P:
            self.change_palette()

        if symbol == pyglet.window.key.S:
            if modifiers & pyglet.window.key.LCTRL:
                self.save_config()

        if symbol == pyglet.window.key.O:
            if modifiers & pyglet.window.key.LCTRL:
                self.load_config()
                self.use_palette(self.palette)
                self.use_pattern(self.pattern)
                
        if symbol == pyglet.window.key.V:
            if modifiers & pyglet.window.key.LCTRL:
                self.switch_video_stats()
                
                
    def save_screenshot(self):
        index = np.random.randint(0, 1000)
        img = pyglet.image.get_buffer_manager().get_color_buffer()
        img.save('screenshot{:05d}.png'.format(index))
        
        
    def save_config(self):
        """Save current config to the json file."""
        with open('config.json', 'a+') as f:
            data = json.dumps({self.pattern: self.palette.tolist()})
            f.write(data + '\n')
            print('> Config saved.\n')
    
    
    def change_palette(self):
        """Use a random palette."""
        alphas = sorted(np.random.random(5))
        palette = np.random.random((5, 4))
        # The first row is set to 0 to make the background black.
        palette[0] = 0.0
        palette[:, -1] = alphas
        palette = palette.round(3)
        self.use_palette(palette)
        self.palette = palette
        print('> Current palette: ')
        print(palette)
        print('\n')

        
    def change_pattern(self):
        """Use the next pattern in the list `_species_names`."""
        index = self._species_names.index(self.pattern)
        next_pattern = self._species_names[(index + 1) % len(self._species_names)]
        self.use_pattern(next_pattern)
        self.pattern = next_pattern
        print('> Current pattern: ' + self.pattern
              + '. If the screen is blank, draw on it!\n')
        
        
    def switch_video_stats(self):
        self.video_on = not self.video_on
        if self.video_on:
            print('start saving frames ...')
        else:
            print('stop saving frames ...')
        self.frame_count = 0
        
        
    def run(self, fps=None):
        """fps: frames per second."""
        self.set_visible(True)
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0/fps)
        pyglet.app.run()
      

if __name__ == '__main__':
    app = GrayScott(width=480, height=320, scale=1, config=1, video=True, mask='PYTHON.png')
    app.run(fps=None)  # use max fps.
