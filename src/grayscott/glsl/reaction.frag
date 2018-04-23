#version 130

in vec2 uv_texcoord;

uniform vec2 u_resolution;
uniform vec2 u_mouse;
uniform sampler2D uv_texture;
uniform sampler2D mask_texture;
uniform vec4 params;

out vec4 result;

void main()
{
    if(u_mouse.x < -5.0)
    {
        result = vec4(1.0, 0.0, 0.0, 1.0);
        return;
    }

    vec2 texel = 1.0 / u_resolution;
    vec2 uv  = texture(uv_texture, uv_texcoord).rg;
    vec2 uv0 = texture(uv_texture, uv_texcoord + vec2(texel.x, 0.0)).rg;
    vec2 uv1 = texture(uv_texture, uv_texcoord + vec2(0.0, texel.y)).rg;
    vec2 uv2 = texture(uv_texture, uv_texcoord + vec2(-texel.x, 0.0)).rg;
    vec2 uv3 = texture(uv_texture, uv_texcoord + vec2(0.0, -texel.y)).rg;

    float Du   = params.x;
    float Dv   = params.y;
    float feed = params.z * texture(mask_texture, uv_texcoord).r;
    float kill = params.w;

    vec2 lapl = uv0 + uv1 + uv2 + uv3 - 4.0 * uv;
    float du = Du * lapl.r - uv.r * uv.g * uv.g + feed * (1.0 - uv.r);
    float dv = Dv * lapl.g + uv.r * uv.g * uv.g - (feed + kill) * uv.g;
    vec2 dst = uv + 0.6 * vec2(du, dv);

    if(u_mouse.x > 0.0)
    {
        vec2 diff = (uv_texcoord - u_mouse) * u_resolution;
        float dist = dot(diff, diff);
        if(dist < 1.0) {dst.g = 0.9;}
    }

    result = vec4(dst, 0.0, 1.0);
}
