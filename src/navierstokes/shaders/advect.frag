# version 130

in vec2 TexCoord;

uniform sampler2D velocity;
uniform sampler2D advectTexture;

uniform float timestep;
uniform float dissipation;
uniform vec2 inverseSize;

out vec4 result;

void main()
{
    vec2 p = texture(velocity, TexCoord).xy;
    vec2 coord = TexCoord - p * timestep * inverseSize;
    result = dissipation * texture(advectTexture, coord);
}
