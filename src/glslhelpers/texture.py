"""
Helper functions for creating textures from images or numpy arrays.
"""
import ctypes as ct

import pyglet
import pyglet.gl as gl
from PIL import Image, ImageOps


def create_texture_from_ndarray(array):
    """Create a 2D texture from a numpy ndarray.
    """
    height, width = array.shape[:2]
    texture = pyglet.image.Texture.create_for_size(
        gl.GL_TEXTURE_2D, width, height, gl.GL_RGBA32F
    )
    gl.glBindTexture(texture.target, texture.id)
    gl.glTexImage2D(
        texture.target,
        texture.level,
        gl.GL_RGBA32F,
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
    You can use either a .png or .jpg file.
    """
    image = pyglet.image.load(imgfile)
    data = image.get_data("RGBA", image.width * 4)
    tex = gl.GLuint()
    gl.glGenTextures(1, ct.pointer(tex))
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
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


def create_cubemap_texture(imgfiles):
    """Create a cubemap texture from image files.

    :param imgfiles: a list of six strings specifying the path to the
        cubemap images. In the order [pos+X, pos-X, pos+Y, ..., pos-Z]
    """
    if len(imgfiles) != 6:
        raise ValueError("exactly six images are required for a cubemap texture")

    # generate a new texture
    cubemap = gl.GLuint()
    gl.glGenTextures(1, ct.pointer(cubemap))

    # bind it to `GL_TEXTURE_CUBE_MAP` and set the filter and wrap mode
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, cubemap)
    gl.glTexParameteri(
        gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR
    )
    gl.glTexParameteri(
        gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR
    )
    gl.glTexParameteri(
        gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE
    )
    gl.glTexParameteri(
        gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE
    )
    gl.glTexParameteri(
        gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE
    )
    # it seems we need to flip the images to make the cubemap look correct
    faces = [ImageOps.flip(Image.open(img)) for img in imgfiles]
    # set the faces of the cubemap texture
    for i, face in enumerate(faces):
        width, height = face.size
        try:
            data = face.tobytes("raw", "RGBX", 0, -1)
        except TypeError:
            data = face.tobytes("raw", "RGBA", 0, -1)

        gl.glTexImage2D(
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
            0,
            gl.GL_RGBA,
            width,
            height,
            0,
            gl.GL_RGBA,
            gl.GL_UNSIGNED_BYTE,
            data,
        )

    gl.glGenerateMipmap(gl.GL_TEXTURE_CUBE_MAP)
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)
    return cubemap
