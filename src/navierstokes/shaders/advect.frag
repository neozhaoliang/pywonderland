# version 130

in vec2 TexCoord;

uniform sampler2D velocityTexture;
uniform sampler2D advectTexture;

uniform float timestep;
uniform float dissipation;
uniform vec2 cellSize;

out vec4 result;

void main()
{
    vec2 p = texture(velocityTexture, TexCoord).xy;
    vec2 coord = TexCoord - p * timestep * cellSize;
    result = dissipation * texture(advectTexture, coord);
}
