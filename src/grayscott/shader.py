import ctypes as ct
import pyglet.gl as gl


class Shader(object):

    def __init__(self, vert_file, frag_file):
        self.program = gl.glCreateProgram()
        self.compile_and_attach_shader(vert_file, gl.GL_VERTEX_SHADER)
        self.compile_and_attach_shader(frag_file, gl.GL_FRAGMENT_SHADER)
        self.link()

    def compile_and_attach_shader(self, shader_file, shader_type):
        """Main steps to compile and attach a shader:
        1. glCreateShader:
                create a shader of given type.
        2. glShaderSource:
                load source code into the shader.
        3. glCompileShader:
                compile the shader.
        4. glGetShaderiv:
                retrieve the compile status.
        5. glGetShaderInfoLog:
                print the error info if compiling failed.
        6. glAttachShader:
                attach the shader to our program if compiling successed.
        """
        with open(shader_file, 'r') as f:
            src = f.read().encode('ascii')

        # 1. create a shader
        shader = gl.glCreateShader(shader_type)

        # 2. load source code into the shader
        src_p = ct.c_char_p(src)
        gl.glShaderSource(shader, 1, ct.cast(ct.pointer(src_p), ct.POINTER(ct.POINTER(ct.c_char))), None)

        # 3. compile the shader
        gl.glCompileShader(shader)

        # 4. retrieve the compile status
        compile_status = gl.GLint(0)
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ct.byref(compile_status))

        # 5. if compiling failed then print the error log
        if not compile_status:
            info_length = gl.GLint(0)
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ct.byref(info_length))
            error_info = ct.create_string_buffer(info_length.value)
            gl.glGetShaderInfoLog(shader, info_length, None, error_info)
            print(error_info.value)

        # 6. else attach the shader to our program
        else:
            gl.glAttachShader(self.program, shader)

    def link(self):
        """Main steps to link the program:
        1. glLinkProgram:
                linke the shaders in the program to create an executable
        2. glGetProgramiv:
                retrieve the link status
        3. glGetProgramInfoLog:
                print the error log if link failed
        """
        gl.glLinkProgram(self.program)

        link_status = gl.GLint(0)
        gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS, ct.byref(link_status))

        if not link_status:
            info_length = gl.GLint(0)
            gl.glGetProgramiv(self.program, gl.GL_INFO_LOG_LENGTH, ct.byref(info_length))
            error_info = ct.create_string_buffer(info_length.value)
            gl.glGetProgramInfoLog(self.program, info_length, None, error_info)
            print(error_info.value)

    def bind(self):
        gl.glUseProgram(self.program)

    def unbind(self):
        gl.glUseProgram(0)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.unbind()

    def set_uniformi(self, name, *vals):
        location = gl.glGetUniformLocation(self.program, name.encode('ascii'))
        { 1: gl.glUniform1i,
          2: gl.glUniform2i,
          3: gl.glUniform3i,
          4: gl.glUniform4i
        }[len(vals)](location, *vals)

    def set_uniformf(self, name, *vals):
        location = gl.glGetUniformLocation(self.program, name.encode('ascii'))
        { 1: gl.glUniform1f,
            2: gl.glUniform2f,
            3: gl.glUniform3f,
            4: gl.glUniform4f
        }[len(vals)](location, *vals)

    def set_uniform_matrix(self, name, mat):
        location = gl.glGetUniformLocation(self.program, name.encode('ascii'))
        gl.glUniformMatrix4fv(location, 1, False, (ct.c_float * 16)(*mat))

    def set_vertex_attrib(self, name, data, size=2, stride=0, offset=0):
        """Set vertex attribute data in a shader, lacks the flexibility of
        setting several attributes in one vertex buffer.

        name: the attribute name in the shader.
        data: a list of vertex attributes (positions, colors, ...)
        example: name = 'positions', data = [0, 0, 0, 1, 1, 0, 1, 1].
        """
        data_ctype = (gl.GLfloat * len(data))(*data)

        vbo_id = gl.GLuint(0)
        gl.glGenBuffers(1, ct.byref(vbo_id))
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, ct.sizeof(data_ctype), data_ctype, gl.GL_STATIC_DRAW)

        location = gl.glGetAttribLocation(self.program, name.encode('ascii'))
        gl.glEnableVertexAttribArray(location)
        gl.glVertexAttribPointer(location, size, gl.GL_FLOAT, gl.GL_FALSE, stride, ct.c_void_p(offset))
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        return vbo_id
