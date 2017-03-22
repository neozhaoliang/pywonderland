# version 130

in vec2 texcoord;
in vec2 position;
out vec2 TexCoord;

void main()
{
    TexCoord = texcoord;
    gl_Position = vec4(position, 0.0, 1.0);
}
