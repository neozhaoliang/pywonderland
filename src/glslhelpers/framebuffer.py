from pyglet.image import Framebuffer as _Framebuffer


class FrameBuffer(_Framebuffer):
    """A simple helper class for handling the frame buffer object (fbo),
    now using pyglet.image.Framebuffer internally.
    """

    def __init__(self):
        super().__init__()

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.unbind()
