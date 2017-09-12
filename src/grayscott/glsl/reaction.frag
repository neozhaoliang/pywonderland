# version 130

in vec2 uv_texcoord;

uniform float dx;
uniform float dy;

uniform float rU;
uniform float rV;

uniform float feed;
uniform float kill;

uniform sampler2D uv_texture;
uniform vec2 u_mouse;

out vec4 result;

void main()
{
    if(u_mouse.x < -5.0)
    {
        result = vec4(1.0, 0.0, 0.0, 1.0);
        return;
    }
    
    vec2 uv  = texture(uv_texture, uv_texcoord).rg;
    vec2 uv0 = texture(uv_texture, uv_texcoord + vec2(dx, 0.0)).rg;
    vec2 uv1 = texture(uv_texture, uv_texcoord + vec2(0.0, dy)).rg;
    vec2 uv2 = texture(uv_texture, uv_texcoord + vec2(-dx, 0.0)).rg;
    vec2 uv3 = texture(uv_texture, uv_texcoord + vec2(0.0, -dy)).rg;

    vec2 lapl = uv0 + uv1 + uv2 + uv3 - 4.0 * uv;
    float du = rU * lapl.r - uv.r * uv.g * uv.g + feed * (1.0 - uv.r);
    float dv = rV * lapl.g + uv.r * uv.g * uv.g - (feed + kill) * uv.g;
    vec2 dst = uv + 0.6 * vec2(du, dv);

    if(u_mouse.x > 0.0)
    {
        vec2 diff = (uv_texcoord - u_mouse) / vec2(dx, dy);
        float dist = dot(diff, diff);
        if(dist < 1.0)
        {  dst.g = 0.9;}

    }

    result = vec4(dst, 0.0, 1.0);
}
