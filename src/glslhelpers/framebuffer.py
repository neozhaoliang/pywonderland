import ctypes as ct
import pyglet.gl as gl


class FrameBuffer:
    """A simple helper class for handling the frame buffer object (fbo).
    """

    def __init__(self):
        self.buff_id = gl.GLuint(0)
        gl.glGenFramebuffersEXT(1, ct.byref(self.buff_id))

    def bind(self):
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.buff_id)

    def unbind(self):
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)

    def attach_texture(self, texture):
        """`texture` must be an instance of pyglet's texture class.
        """
        gl.glFramebufferTexture2DEXT(
            gl.GL_FRAMEBUFFER_EXT,
            gl.GL_COLOR_ATTACHMENT0_EXT,
            texture.target,
            texture.id,
            texture.level,
        )

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.unbind()
