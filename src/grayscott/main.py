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


palette = [(0.0, 0.0, 0.0, 0.0),
           (0.0, 1.0, 0.0, 0.2),
           (1.0, 1.0, 0.0, 0.21),
           (1.0, 0.0, 0.0, 0.4),
           (1.0, 1.0, 1.0, 0.6)]

species = {'spots and loops': [0.2097, 0.105, 0.018, 0.051],
           'zebrafish': [0.16, 0.08, 0.035, 0.060],
           'solitons': [0.14, 0.06, 0.035, 0.065],
           'coral': [0.16, 0.08, 0.060, 0.062],
           'fingerprint' : [0.19, 0.05, 0.060, 0.062],
           'worm': [0.16, 0.08, 0.050, 0.065]}

reaction_shader = Shader.from_files('reaction.vert', 'reaction.frag')
render_shader = Shader.from_files('render.vert', 'render.frag')


def GrayScott(width, height, scale, pattern):
    window = pyglet.window.Window(width, height, caption='GrayScott Simullation',
                                  visible=False, vsync=False)
    window.set_location(100, 100)
    width //= scale
    height //= scale
    
    rU, rV, feed, kill = species[pattern]
    with reaction_shader:
        reaction_shader.set_uniformi('uv_texture', 0)
        reaction_shader.set_uniformf('dx', 1.0/width)
        reaction_shader.set_uniformf('dy', 1.0/height)
        reaction_shader.set_uniformf('feed', feed)
        reaction_shader.set_uniformf('kill', kill)
        reaction_shader.set_uniformf('rU', rU)
        reaction_shader.set_uniformf('rV', rV)
        reaction_shader.set_vertex_attrib('position', [(-1, -1), (1, -1), (1, 1,), (-1, 1)])
        reaction_shader.set_vertex_attrib('texcoord', [(0, 0), (1, 0), (1, 1,), (0, 1)])

    with render_shader:
        render_shader.set_uniformi('uv_texture', 0)
        render_shader.set_uniformf('color1', *palette[0])
        render_shader.set_uniformf('color2', *palette[1])
        render_shader.set_uniformf('color3', *palette[2])
        render_shader.set_uniformf('color4', *palette[3])
        render_shader.set_uniformf('color5', *palette[4])
        render_shader.set_vertex_attrib('position', [(-1, -1), (1, -1), (1, 1,), (-1, 1)])
        render_shader.set_vertex_attrib('texcoord', [(0, 0), (1, 0), (1, 1,), (0, 1)])
        
    uv_grid = np.zeros((height,width,4), dtype=np.float32)
    uv_grid[:,:,0] = 1.0
    r = 32
    uv_grid[height/2-r : height/2+r,  width/2-r : width/2+r,  0] = 0.50
    uv_grid[height/2-r : height/2+r,  width/2-r : width/2+r,  1] = 0.25
    uv_texture = create_texture_from_array(uv_grid)
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(uv_texture.target, uv_texture.id)

    with FrameBuffer() as fbo:
        fbo.attach_texture(uv_texture)

        
    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot{:03d}.png'.format(np.random.randint(0, 1000)))
            
           
    @window.event
    def on_draw():
        gl.glClearColor(0, 0, 0, 0)
        window.clear()
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, 1, 0, 1, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        with fbo:
            with reaction_shader:
                gl.glDrawArrays(gl.GL_QUADS, 0, 4)

        gl.glViewport(0, 0, window.width, window.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, 1, 0, 1, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        with render_shader:
            gl.glDrawArrays(gl.GL_QUADS, 0, 4)
            


    pyglet.clock.schedule(lambda dt: None)
    window.set_visible(True)
    pyglet.app.run()


if __name__ == '__main__':
    print('press \'ENTER\' to save snapshots, or \'ESC\' to exit')
    GrayScott(600, 400, 2, 'spots and loops')
