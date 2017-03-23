# version 130

in vec2 TexCoord;

uniform sampler2D pressure;
uniform sampler2D divergence;
uniform float alpha;
uniform float rBeta;
uniform vec2 cellSize;

out vec4 result;

void main()
{
    vec4 left   = texture(pressure, TexCoord - vec2(cellSize.x, 0));
    vec4 right  = texture(pressure, TexCoord + vec2(cellSize.x, 0));
    vec4 down   = texture(pressure, TexCoord - vec2(0, cellSize.y));
    vec4 up     = texture(pressure, TexCoord + vec2(0, cellSize.y));
    vec4 center = texture(divergence, TexCoord); 

    result = (left + right + up + down + alpha * center) * rBeta;
}
