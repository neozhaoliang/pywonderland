in vec2 Texcoord;

uniform float iTime;

out vec4 finalColor;

void main()
{
    finalColor = vec4(Texcoord.x * sin(iTime), Texcoord.y * cos(iTime), 0.8, 1.0);
}
