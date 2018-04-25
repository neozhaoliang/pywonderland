in vec2 Texcoord;

uniform float iTime;

out vec4 finalColor;

#define PI 3.141592653
#define TWOPI (2 * PI)

/*
    Convert hsv color to rgb color
*/

vec3 hsv2rgb(vec3 hsv)
{
    const vec3 p = vec3(0.0, 2.0/3.0, 1.0/3.0);
    hsv.yz = clamp(hsv.yz, 0.0, 1.0);
    return hsv.z * (0.63 * hsv.y * (cos(TWOPI *(hsv.x + p)) - 1.0) + 1.0);
}


void main()
{
    vec2 p = C_Mult(Texcoord, vec2(sin(iTime), cos(iTime)));
    vec3 color = hsv2rgb(vec3(p, 0.8));
    finalColor = vec4(color, 1.0);
}
