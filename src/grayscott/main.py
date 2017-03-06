# pylint: disable = unused-argument
'''
A GrayScott reaction-diffusion simulator written with pyglet and GLSL.

This program is motivated by pmneila's Javascript project:

    "http://pmneila.github.io/jsexp/grayscott/"


Usage: just run

    python main.py

and enjoy the result!
'''
import json
import numpy as np
import pyglet
pyglet.options['debug_gl'] = False
import pyglet.gl as gl
from shader import Shader
from framebuffer import FrameBuffer


def create_texture_from_array(array):
    '''
    create a pyglet texture instance from a numpy ndarray.
    '''
    height, width = array.shape[:2]
    texture = pyglet.image.Texture.create_for_size(gl.GL_TEXTURE_2D, width, height, gl.GL_RGBA32F_ARB)
    gl.glBindTexture(texture.target, texture.id)
    gl.glTexImage2D(texture.target, texture.level, gl.GL_RGBA32F_ARB,
                    width, height, 0, gl.GL_RGBA, gl.GL_FLOAT, array.ctypes.data)
    gl.glBindTexture(texture.target, 0)
    return texture


class GrayScott(pyglet.window.Window):

    '''
    This simulation uses mouse and keyboard to control the patterns and colors.
    At any time you may click or drag your mouse to draw on the screen.

    Keyboad control:
        1. press 'space' to clear the window to blank.
        2. press 'p' to change to a random palette.
        4. press 's' to change to another pattern.
        5. press 'r' to reset to default.
        6. press 'ctrl + s' to save current config to json file.
        7. press 'ctrl + o' to load config from json file.
        8. press 'Enter' to take screenshots.
        9. press 'Esc' to exit.
    '''

    # pattern: [rU, rV, feed, kill]
    # parameters from http://www.aliensaint.com/uo/java/rd/
    species = {'bacteria1':       [0.16, 0.08, 0.035, 0.065],
               'bacteria2':       [0.14, 0.06, 0.035, 0.065],
               'coral':           [0.16, 0.08, 0.060, 0.062],
               'fingerprint':     [0.19, 0.05, 0.060, 0.062],
               'spirals':         [0.10, 0.10, 0.018, 0.050],
               'spirals_dense':   [0.12, 0.08, 0.020, 0.050],
               'spirals_fast':    [0.10, 0.16, 0.020, 0.050],
               'unstable':        [0.16, 0.08, 0.020, 0.055],
               'worms1':          [0.16, 0.08, 0.050, 0.065],
               'worms2':          [0.16, 0.08, 0.054, 0.063],
               'zebrafish':       [0.16, 0.08, 0.035, 0.060],
              }

    # palette will be used for coloring the uv_texture.
    palette_default = [(0.0, 0.0, 0.0, 0.0),
                       (0.0, 1.0, 0.0, 0.2),
                       (1.0, 1.0, 0.0, 0.21),
                       (1.0, 0.0, 0.0, 0.4),
                       (1.0, 1.0, 1.0, 0.6)]


    def __init__(self, width, height, pattern, scale=2):
        '''
        width, height:
            size of the window in pixels.
        scale:
            the size of the texture is (width//scale) x (height//scale).
        pattern:
            a name in dict 'species'.
        '''
        pyglet.window.Window.__init__(self, width, height, caption='GrayScott Simulation',
                                      visible=False, vsync=False)

        # we will need two shaders, one for computing the reaction and diffusion,
        # and one for coloring the uv_texture.
        self.reaction_shader = Shader.from_files('default.vert', 'reaction.frag')
        self.render_shader = Shader.from_files('default.vert', 'render.frag')
        self.pattern = pattern
        self.palette = GrayScott.palette_default
        self.tex_width = width // scale
        self.tex_height = height // scale
        self.uv_texture = self.create_texture(width//scale, height//scale)

        # set the uniforms and attributes in the two shaders.
        self.set_reation_shader()
        self.set_render_shader()

        # we need a framebuffer to do the offscreen rendering.
        # once we finished computing the reaction-diffusion step with the reaction_shader,
        # we render the result to this 'invisible' buffer since we do not want to show it.
        # the final image is further colored and will be rendered to the window.
        with FrameBuffer() as self.fbo:
            self.fbo.attach_texture(self.uv_texture)

        # why do we need this?
        # the reason is in the 'on_mouse_drag' function.
        self.mouse_down = False


    def create_texture(self, width, height):
        uv_grid = np.zeros((height, width, 4), dtype=np.float32)
        uv_grid[:, :, 0] = 1.0
        r = 32
        uv_grid[height//2-r : height//2+r, width//2-r : width//2+r, 0] = 0.50
        uv_grid[height//2-r : height//2+r, width//2-r : width//2+r, 1] = 0.25
        uv_texture = create_texture_from_array(uv_grid)
        # the texture is bind to unit '0'.
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(uv_texture.target, uv_texture.id)
        return uv_texture


    def set_reation_shader(self):
        with self.reaction_shader:
            self.reaction_shader.set_uniformi('uv_texture', 0)
            self.reaction_shader.set_uniformf('dx', 1.0/self.tex_width)
            self.reaction_shader.set_uniformf('dy', 1.0/self.tex_height)
            # the order of the vertices and texcoords matters,
            # since we will call 'GL_TRIANGLE_STRIP' to draw them.
            self.reaction_shader.set_vertex_attrib('position', [(-1, -1), (1, -1), (-1, 1,), (1, 1)])
            self.reaction_shader.set_vertex_attrib('texcoord', [(0, 0), (1, 0), (0, 1), (1, 1)])
            self.reaction_shader.set_uniformf('brush', -1, -1)

        self.set_pattern(self.pattern)


    def set_pattern(self, pattern):
        rU, rV, feed, kill = GrayScott.species[pattern]
        with self.reaction_shader:
            self.reaction_shader.set_uniformf('feed', feed)
            self.reaction_shader.set_uniformf('kill', kill)
            self.reaction_shader.set_uniformf('rU', rU)
            self.reaction_shader.set_uniformf('rV', rV)


    def set_render_shader(self):
        with self.render_shader:
            self.render_shader.set_uniformi('uv_texture', 0)
            self.render_shader.set_vertex_attrib('position', [(-1, -1), (1, -1), (-1, 1), (1, 1)])
            self.render_shader.set_vertex_attrib('texcoord', [(0, 0), (1, 0), (0, 1), (1, 1)])

        self.set_palette(self.palette)


    def set_palette(self, palette):
        self.palette = palette
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

        # since we are rendering to the invisible framebuffer, the size is just the texture's size.
        self.set_viewport(self.tex_width, self.tex_height)
        with self.fbo:
            with self.reaction_shader:
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        # now we render to the actual window, hence the size is window's size.
        self.set_viewport(self.width, self.height)
        with self.render_shader:
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)


    def on_key_press(self, symbol, modifiers):
        # take screenshots
        if symbol == pyglet.window.key.ENTER:
            index = np.random.randint(0, 1000)
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot{:03d}.png'.format(index))

        # exit the simulation
        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()

        # clear to blank window
        if symbol == pyglet.window.key.SPACE:
            self.update_brush(-10,- 10)

        # change to a random pattern
        if symbol == pyglet.window.key.S:
            if not modifiers:
                pattern = self.pattern
                while pattern == self.pattern:
                    self.pattern = np.random.choice(list(GrayScott.species.keys()))
                self.set_pattern(pattern)
                print('current pattern: ' + pattern + ' , draw on it!')


        # change to a random palette
        if symbol == pyglet.window.key.P:
            self.set_random_palette()

        # reset to default config
        if symbol == pyglet.window.key.R:
            if modifiers & pyglet.window.key.LCTRL:
                self.set_palette(GrayScott.palette_default)
                self.set_pattern('bacteria2')

        # save current config to the json file
        if symbol == pyglet.window.key.S:
            if modifiers & pyglet.window.key.LCTRL:
                with open('palette.json', 'a+') as f:
                    data = json.dumps({self.pattern: self.palette.tolist()})
                    f.write(data + '\n')
                print('config saved')

        # load a config from the json file.
        if symbol == pyglet.window.key.O:
            if modifiers & pyglet.window.key.LCTRL:
                num = input('enter the line numer in json file: ')
                with open('palette.json', 'r') as f:
                    for i, line in enumerate(f, start=1):
                        if i == int(num):
                            data = json.loads(line)
                            for key, item in data.items():
                                self.set_pattern(key)
                                self.set_palette(item)
                                print('if it is a blank screen, draw on it!')


    def on_mouse_press(self, x, y, button, modifiers):
        '''
        press mouse to add 'v'.
        '''
        self.mouse_down = True
        bx = x / float(self.width)
        by = y / float(self.height)
        self.update_brush(bx, by)


    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_down = False
        self.update_brush(-1, -1)


    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.mouse_down:
            bx = x / float(self.width)
            by = y / float(self.height)
            self.update_brush(bx, by)


    def update_brush(self, *brush):
        self.set_viewport(self.tex_width, self.tex_height)
        with self.fbo:
            with self.reaction_shader:
                self.reaction_shader.set_uniformf('brush', *brush)
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)


    def set_random_palette(self):
        alphas = sorted(np.random.random(5))
        palette = np.random.random((5, 4))
        palette[0] = 0.0
        #palette[-1] = 1.0
        palette[:, -1] = alphas
        print('current palette:')
        print(palette)
        self.set_palette(palette)


    def run(self):
        self.set_visible(True)
        pyglet.clock.schedule(lambda dt: None)
        pyglet.app.run()



if __name__ == '__main__':
    app = GrayScott(width=600, height=480, scale=2, pattern='unstable')
    print(app.__doc__)
    app.run()
