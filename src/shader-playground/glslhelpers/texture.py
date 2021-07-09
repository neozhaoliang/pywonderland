"""
Helper functions for creating textures from images or numpy arrays.
"""
import ctypes as ct
import pyglet
import pyglet.gl as gl


def create_texture_from_ndarray(array):
    """Create a 2D texture from a numpy ndarray.
    """
    height, width = array.shape[:2]
    texture = pyglet.image.Texture.create_for_size(
        gl.GL_TEXTURE_2D, width, height, gl.GL_RGBA32F_ARB
    )
    gl.glBindTexture(texture.target, texture.id)
    gl.glTexImage2D(
        texture.target,
        texture.level,
        gl.GL_RGBA32F_ARB,
        width,
        height,
        0,
        gl.GL_RGBA,
        gl.GL_FLOAT,
        array.ctypes.data,
    )
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glBindTexture(texture.target, 0)
    return texture


def create_image_texture(imgfile):
    """Create a 2D texture from an image file.
    """
    image = pyglet.image.load(imgfile)
    data = image.get_data("RGBA", image.width * 4)
    tex = gl.GLuint()
    gl.glGenTextures(1, ct.pointer(tex))
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGBA,
        image.width,
        image.height,
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        data,
    )
    gl.glBindTexture(tex, 0)
    return tex
