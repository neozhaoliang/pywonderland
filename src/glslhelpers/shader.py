import ctypes as ct
import pyglet.gl as gl
from pyglet.graphics.shader import Shader as GLShader, ShaderProgram as GLShaderProgram


class Shader(GLShaderProgram):
    """A helper class for compiling and communicating with shader programs."""

    def __init__(self, vert_files, frag_files):
        vert_src_list = []
        for src_f in vert_files:
            with open(src_f, "r", encoding="utf-8") as f:
                vert_src_list.append(f.read())
        frag_src_list = []
        for src_f in frag_files:
            with open(src_f, "r", encoding="utf-8") as f:
                frag_src_list.append(f.read())

        vert_src = "\n".join(vert_src_list)
        frag_src = "\n".join(frag_src_list)

        vert_shader = GLShader(vert_src, "vertex")
        frag_shader = GLShader(frag_src, "fragment")
        super().__init__(vert_shader, frag_shader)

        self.program = self.id
        self._mode = gl.GL_TRIANGLE_STRIP

        vdata = {}
        quad = (
            -1.0,
            -1.0,
            1.0,
            -1.0,
            -1.0,
            1.0,
            1.0,
            1.0,
        )

        if "position" in self.attributes:
            vdata["position"] = ("f", quad)

        if "texcoord" in self.attributes:
            texcoords = (
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                1.0,
                1.0,
                1.0,
            )
            vdata["texcoord"] = ("f", texcoords)

        # 真正创建 VertexList
        self._vlist = None
        if vdata:
            self._vlist = self.vertex_list(
                4,
                self._mode,
                **vdata,
            )

    def bind(self):
        gl.glUseProgram(self.program)

    def unbind(self):
        gl.glUseProgram(0)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.unbind()

    def _get_uniform_location(self, name: str) -> int:
        return gl.glGetUniformLocation(self.program, name.encode("ascii"))

    def uniformi(self, name, *data):
        loc = self._get_uniform_location(name)
        if loc < 0:
            return
        func = {
            1: gl.glUniform1i,
            2: gl.glUniform2i,
            3: gl.glUniform3i,
            4: gl.glUniform4i,
        }[len(data)]
        func(loc, *data)

    def uniformf(self, name, *data):
        loc = self._get_uniform_location(name)
        if loc < 0:
            return
        func = {
            1: gl.glUniform1f,
            2: gl.glUniform2f,
            3: gl.glUniform3f,
            4: gl.glUniform4f,
        }[len(data)]
        func(loc, *[float(v) for v in data])

    def uniformfv(self, name, size, data):
        loc = self._get_uniform_location(name)
        if loc < 0:
            return
        data_ctype = (gl.GLfloat * len(data))(*data)
        {
            1: gl.glUniform1fv,
            2: gl.glUniform2fv,
            3: gl.glUniform3fv,
            4: gl.glUniform4fv,
        }[len(data) // size](loc, size, data_ctype)

    def draw(self):
        if self._vlist is not None:
            self._vlist.draw(self._mode)
