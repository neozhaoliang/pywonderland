"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Limit set of rank 4 hyperbolic groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import sys

sys.path.append("../glslhelpers")

import time

import pyglet

pyglet.options["debug_gl"] = False
import pyglet.gl as gl
import pyglet.window.key as key
from shader import Shader
from texture import create_image_texture


metal_texture_image = "../glslhelpers/textures/rusty_metal.jpg"


class LimitSet(pyglet.window.Window):
    """
    Keyboard control:
        1. use mouse drag to transform the pattern.
        2. set other PQRs to view different patterns.
        3. press Enter to save screenshots.
        4. press Esc to exit.
    """

    def __init__(self, width, height, PQR):
        """
        :param width & height: size of the main window in pixels.
        """
        pyglet.window.Window.__init__(
            self,
            width,
            height,
            caption="Hyperbolic limit set",
            resizable=True,
            visible=False,
            vsync=False,
        )
        self._start_time = time.clock()
        self.shader = Shader(["./glsl/main.vert"], ["./glsl/main.frag"])
        self.PQR = PQR

        metal_tex = create_image_texture(metal_texture_image)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, metal_tex)
        with self.shader:
            self.shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.uniformf("iResolution", self.width, self.height, 0.0)
            self.shader.uniformf("iTime", 0.0)
            self.shader.uniformf("PQR", *self.PQR)
            self.shader.uniformi("iChannel0", 0)
            self.shader.uniformf("iMouse", 0, 0, 0, 0)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        with self.shader:
            self.shader.uniformf("iTime", time.clock() - self._start_time)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def save_screenshot(self):
        buff = pyglet.image.get_buffer_manager().get_color_buffer()
        buff.save("hyperbolic-limit-set.png")

    def on_mouse_press(self, x, y, button, modifiers):
        if button & pyglet.window.mouse.LEFT:
            with self.shader:
                self.shader.uniformf("iMouse", x, y, x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        """Don't forget reset 'iMouse' when mouse is released.
        """
        with self.shader:
            self.shader.uniformf("iMouse", 0, 0, 0, 0)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button & pyglet.window.mouse.LEFT:
            with self.shader:
                x += dx
                y += dy
                x = max(min(x, self.width), 0)
                y = max(min(y, self.height), 0)
                self.shader.uniformf("iMouse", x, y, x, y)

    def run(self, fps=None):
        self.set_visible(True)
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0 / fps)
        pyglet.app.run()


if __name__ == "__main__":
    app = LimitSet(width=1080, height=720, PQR=(6, 3, 100000))
    print(app.__doc__)
    app.run()
