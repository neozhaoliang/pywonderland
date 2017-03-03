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


# pattern: [rU, rV, feed, kill]
species = { 'spots_and_loops': [0.2097, 0.105, 0.018, 0.051],
            'zebrafish':       [0.16, 0.08, 0.035, 0.060],
            'solitons':        [0.14, 0.06, 0.035, 0.065],
            'coral':           [0.16, 0.08, 0.060, 0.062],
            'fingerprint' :    [0.19, 0.05, 0.060, 0.062],
            'worm':            [0.16, 0.08, 0.050, 0.065],
}

# palette will be used for coloring the uv_texture.
palette = [(0.0, 0.0, 0.0, 0.0),
           (0.0, 1.0, 0.0, 0.2),
           (1.0, 1.0, 0.0, 0.21),
           (1.0, 0.0, 0.0, 0.4),
           (1.0, 1.0, 1.0, 0.6)]

# we will need two shaders, one for computing the reaction and diffusion,
# and one for coloring the uv_texture.
reaction_shader = Shader.from_files('reaction.vert', 'reaction.frag')
render_shader = Shader.from_files('render.vert', 'render.frag')


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


def GrayScott(width, height, scale, pattern):
    '''
    width, height:
        size of the window in pixels.
    
    scale:
        determines the size of the grid.
        the grid will be of size (width//scale) x (height//scale)

    pattern:
        must be one of 'solitons', 'worms', 'spots_and_loops', etc. 
    '''
    window = pyglet.window.Window(width, height, caption='GrayScott Simullation',
                                  visible=False, vsync=False)
    window.set_location(100, 100)
    width //= scale
    height //= scale

    # now we set the uniforms and attributes in the two shaders.
    rU, rV, feed, kill = species[pattern]
    with reaction_shader:
        reaction_shader.set_uniformi('uv_texture', 0)
        reaction_shader.set_uniformf('dx', 1.0/width)
        reaction_shader.set_uniformf('dy', 1.0/height)
        reaction_shader.set_uniformf('feed', feed)
        reaction_shader.set_uniformf('kill', kill)
        reaction_shader.set_uniformf('rU', rU)
        reaction_shader.set_uniformf('rV', rV)
        # the order of the vertices and texcoords matters,
        # since we will call 'GL_TRIANGLE_STRIP' to draw them.
        reaction_shader.set_vertex_attrib('position', [(-1, -1), (1, -1), (-1, 1,), (1, 1)])
        reaction_shader.set_vertex_attrib('texcoord', [(0, 0), (1, 0), (0, 1), (1, 1)])

    with render_shader:
        render_shader.set_uniformi('uv_texture', 0)
        render_shader.set_uniformf('color1', *palette[0])
        render_shader.set_uniformf('color2', *palette[1])
        render_shader.set_uniformf('color3', *palette[2])
        render_shader.set_uniformf('color4', *palette[3])
        render_shader.set_uniformf('color5', *palette[4])
        render_shader.set_vertex_attrib('position', [(-1, -1), (1, -1), (-1, 1), (1, 1)])
        render_shader.set_vertex_attrib('texcoord', [(0, 0), (1, 0), (0, 1), (1, 1)])

    uv_grid = np.zeros((height, width, 4), dtype=np.float32)
    uv_grid[:, :, 0] = 1.0
    r = 32
    uv_grid[height//2-r : height//2+r,  width//2-r : width//2+r,  0] = 0.50
    uv_grid[height//2-r : height//2+r,  width//2-r : width//2+r,  1] = 0.25
    uv_texture = create_texture_from_array(uv_grid)
    # the texture is bind to unit '0'.
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(uv_texture.target, uv_texture.id)

    # we need a framebuffer to do the offscreen rendering.
    # once we finished computing the reaction-diffusion step with the reaction_shader,
    # we render the result to this 'invisible' buffer since we do not want to show it.
    # the final image is further colored by the render_shader and will be rendered to the window.
    with FrameBuffer() as fbo:
        fbo.attach_texture(uv_texture)

    @window.event
    def on_key_press(symbol, modifiers):
        '''
        prese 'Enter' to take snapshots.
        '''
        if symbol == pyglet.window.key.ENTER:
            index = np.random.randint(0, 1000)
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot{:03d}.png'.format(index))

    @window.event
    def on_draw():
        gl.glClearColor(0, 0, 0, 0)
        window.clear()
        # since we are rendering to the invisible framebuffer, the size is just the texture's size. 
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, 1, 0, 1, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        with fbo:
            with reaction_shader:
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        # now we render to the actual window, hence the size is window's size.
        gl.glViewport(0, 0, window.width, window.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, 1, 0, 1, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        with render_shader:
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    pyglet.clock.schedule(lambda dt: None)
    window.set_visible(True)
    pyglet.app.run()


if __name__ == '__main__':
    print('press \'ENTER\' to save snapshots, or \'ESC\' to exit')
    GrayScott(600, 400, 2, 'solitons')
