# pylint: disable = unused-variable
'''
A GrayScott reaction-diffusion simulator written with pyglet and GLSL.

This program is motivated by pmneila's Javascript project:

    "http://pmneila.github.io/jsexp/grayscott/"


Usage: just run

    python main.py

and enjoy the result!
'''
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
    Kerboard and mouse control:
        1. press 'Enter' to take screenshots.
        2. click or drag your mouse to disturb the pattern.
        3. press 'Esc' to exit.
    '''

    # pattern: [rU, rV, feed, kill]
    species = { 'spots_and_loops': [0.2097, 0.105, 0.018, 0.051],
                'zebrafish':       [0.16, 0.08, 0.035, 0.060],
                'solitons':        [0.14, 0.06, 0.035, 0.065],
                'coral':           [0.16, 0.08, 0.060, 0.062],
                'fingerprint' :    [0.19, 0.05, 0.060, 0.062],
                'worms':           [0.16, 0.08, 0.050, 0.065],
    }

    # palette will be used for coloring the uv_texture.
    palette = [(0.0, 0.0, 0.0, 0.0),
               (0.0, 1.0, 0.0, 0.2),
               (1.0, 1.0, 0.0, 0.21),
               (1.0, 0.0, 0.0, 0.4),
               (1.0, 1.0, 1.0, 0.6)]
    
    def __init__(self, width, height, scale, pattern):
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
        self.tex_width = width // scale
        self.tex_height = height // scale
        self.uv_texture = self.create_texture(width//scale, height//scale)

        # set the uniforms and attributes in the two shaders.
        self.set_shader_data(pattern)

        # we need a framebuffer to do the offscreen rendering.
        # once we finished computing the reaction-diffusion step with the reaction_shader,
        # we render the result to this 'invisible' buffer since we do not want to show it.
        # the final image is further colored by the render_shader and will be rendered to the window.
        with FrameBuffer() as self.fbo:
            self.fbo.attach_texture(self.uv_texture)

        # why do we need this?
        # the reason is in the 'on_mouse_drag' function. 
        self.mouse_down = False


    def create_texture(self, width, height):
        uv_grid = np.zeros((height, width, 4), dtype=np.float32)
        uv_grid[:, :, 0] = 1.0
        r = 32
        uv_grid[height//2-r : height//2+r,  width//2-r : width//2+r,  0] = 0.50
        uv_grid[height//2-r : height//2+r,  width//2-r : width//2+r,  1] = 0.25
        uv_texture = create_texture_from_array(uv_grid)
        # the texture is bind to unit '0'.
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(uv_texture.target, uv_texture.id)
        return uv_texture


    def set_shader_data(self, pattern):
        rU, rV, feed, kill = GrayScott.species[pattern]
        color1, color2, color3, color4, color5 = GrayScott.palette
        
        with self.reaction_shader:
            self.reaction_shader.set_uniformi('uv_texture', 0)
            self.reaction_shader.set_uniformf('dx', 1.0/self.tex_width)
            self.reaction_shader.set_uniformf('dy', 1.0/self.tex_height)
            self.reaction_shader.set_uniformf('feed', feed)
            self.reaction_shader.set_uniformf('kill', kill)
            self.reaction_shader.set_uniformf('rU', rU)
            self.reaction_shader.set_uniformf('rV', rV)
            self.reaction_shader.set_uniformf('brush', -1, -1)
            # the order of the vertices and texcoords matters,
            # since we will call 'GL_TRIANGLE_STRIP' to draw them.
            self.reaction_shader.set_vertex_attrib('position', [(-1, -1), (1, -1), (-1, 1,), (1, 1)])
            self.reaction_shader.set_vertex_attrib('texcoord', [(0, 0), (1, 0), (0, 1), (1, 1)])

        with self.render_shader:
            self.render_shader.set_uniformi('uv_texture', 0)
            self.render_shader.set_uniformf('color1', *color1)
            self.render_shader.set_uniformf('color2', *color2)
            self.render_shader.set_uniformf('color3', *color3)
            self.render_shader.set_uniformf('color4', *color4)
            self.render_shader.set_uniformf('color5', *color5)
            self.render_shader.set_vertex_attrib('position', [(-1, -1), (1, -1), (-1, 1), (1, 1)])
            self.render_shader.set_vertex_attrib('texcoord', [(0, 0), (1, 0), (0, 1), (1, 1)])


    def set_view(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, 1, 0, 1, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)


    def run(self):
        self.set_visible(True)
        pyglet.clock.schedule(lambda dt: None)
        pyglet.app.run()


    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()

        # since we are rendering to the invisible framebuffer, the size is just the texture's size.
        self.set_view(self.tex_width, self.tex_height)
        with self.fbo:
            with self.reaction_shader:
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        # now we render to the actual window, hence the size is window's size.
        self.set_view(self.width, self.height)
        with self.render_shader:
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)


    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            index = np.random.randint(0, 1000)
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot{:03d}.png'.format(index))


    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_down = True
        bx = x / float(self.width)
        by = y / float(self.height)
        self.set_view(self.tex_width, self.tex_height)
        with self.fbo:
            with self.reaction_shader:
                self.reaction_shader.set_uniformf('brush', bx, by)
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)


    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_down = False
        bx = x / float(self.width)
        by = y / float(self.height)
        self.set_view(self.tex_width, self.tex_height)
        with self.fbo:
            with self.reaction_shader:
                self.reaction_shader.set_uniformf('brush', -1, -1)
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)


    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        '''
        when dragging the mouse, it jumps between 'mouse up' and 'mouse down'.
        '''
        if self.mouse_down:
            bx = (x + dx) / float(self.width)
            by = (y + dy) / float(self.height)
            self.set_view(self.tex_width, self.tex_height)
            with self.fbo:
                with self.reaction_shader:
                    self.reaction_shader.set_uniformf('brush', bx, by)
                    gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
 

if __name__ == '__main__':
    app = GrayScott(width=600, height=480, scale=2, pattern='zebrafish')
    print(app.__doc__)
    app.run()
