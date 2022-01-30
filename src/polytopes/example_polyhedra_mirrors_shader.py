"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Shader animation of polyhedron mirrors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import sys
sys.path.append("../")

import os
import time
import pyglet
pyglet.options["debug_gl"] = False

import numpy as np
import pyglet.gl as gl
import pyglet.window.key as key

from polytopes import models
from glslhelpers import Shader, create_cubemap_texture, create_image_texture


WOOD_IMAGE = "../glslhelpers/textures/wood.jpg"
CUBEMAP_IMAGES = [
    f"../glslhelpers/textures/st_peters{i}.png" for i in range(6)
]
GLSL_DIR = "./glsl/mirrors"


def generate_polytope_data(
        coxeter_diagram,
        trunc_type,
        extra_relations=(),
        snub=False,
        dual=False
):
    """
    Generate polyhedra vertex coordinates and face indices.
    The result is output to the file `data.frag`.
    """
    if snub:
        P = models.Snub(coxeter_diagram, extra_relations=extra_relations)
    else:
        P = models.Polyhedra(coxeter_diagram, trunc_type, extra_relations)

    if dual:
        P = models.Catalan3D(P)

    P.build_geometry()
    vertices_coords = P.vertices_coords

    def get_oriented_faces(face_group, name):
        """The faces returned by `P.build_geometry()` may not have their
        normal vectors pointing outward, we need to rearange them in the
        right order before sending them to the gpu.
        """
        m = len(face_group)
        n = len(face_group[0])
        faces_data = np.zeros((m, n, 3), dtype=float)
        for ind, face in enumerate(face_group):
            face_coords = [vertices_coords[ind] for ind in face]
            face_center = sum(face_coords) / len(face)
            v0, v1, v2 = face_coords[:3]
            normal = np.cross(v1 - v0, v2 - v0)
            if np.dot(face_center, normal) < 0:
                face_coords = face_coords[::-1]

            faces_data[ind, :, :] = face_coords

        faces_data = faces_data.reshape(m * n, 3)
        vec_string = ",\n".join(
            f"    vec3({x}, {y}, {z})" for x, y, z in faces_data
        )
        return (f"#define {name}Enabled  {n}\n\n" +
                f"vec3[{m * n}] {name} = vec3[{m * n}](\n{vec_string}\n);\n\n")

    result = get_oriented_faces(P.face_indices[0], "facesA")

    if len(P.face_indices) > 1:
        result += get_oriented_faces(P.face_indices[1], "facesB")
    if len(P.face_indices) > 2:
        result += get_oriented_faces(P.face_indices[2], "facesC")

    with open(os.path.join(GLSL_DIR, "data.frag"), "w") as f:
        f.write(result)


class PolyhedraMirror(pyglet.window.Window):
    """
    Keyboard control:
        1. press Enter to save screenshots.
        2. press Esc to exit.
    """

    def __init__(self, width, height):
        """:param width & height: size of the main window in pixels.
        """
        pyglet.window.Window.__init__(
            self,
            width,
            height,
            caption="Polyhedra Mirrors",
            resizable=True,
            visible=False,
            vsync=False,
        )
        self._start_time = time.perf_counter()
        self.shader = Shader(
            [os.path.join(GLSL_DIR, "default.vert")],
            [os.path.join(GLSL_DIR, "common.frag"),
             os.path.join(GLSL_DIR, "data.frag"),
             os.path.join(GLSL_DIR, "main.frag")
            ]
        )

        wood = create_image_texture(WOOD_IMAGE)
        cubemap = create_cubemap_texture(CUBEMAP_IMAGES)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, cubemap)

        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, wood)

        with self.shader:
            self.shader.vertex_attrib("position", [-1, -1, 1, -1, -1, 1, 1, 1])
            self.shader.uniformf("iResolution", self.width, self.height, 0.0)
            self.shader.uniformf("iTime", 0.0)
            self.shader.uniformi("iChannel0", 0)
            self.shader.uniformi("iChannel1", 1)

    def on_draw(self):
        gl.glClearColor(0, 0, 0, 0)
        self.clear()
        gl.glViewport(0, 0, self.width, self.height)
        with self.shader:
            self.shader.uniformf("iTime", time.perf_counter() - self._start_time)
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            self.save_screenshot()

        if symbol == key.ESCAPE:
            pyglet.app.exit()

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

    def save_screenshot(self):
        buff = pyglet.image.get_buffer_manager().get_color_buffer()
        buff.save("screenshot.png")

    def run(self, fps=None):
        self.set_visible(True)
        if fps is None:
            pyglet.clock.schedule(lambda dt: None)
        else:
            pyglet.clock.schedule_interval(lambda dt: None, 1.0 / fps)
        pyglet.app.run()


if __name__ == "__main__":
    generate_polytope_data((5, 2, 3), (1, 1, 1))
    app = PolyhedraMirror(width=800, height=600)
    print(app.__doc__)
    app.run(fps=60)
