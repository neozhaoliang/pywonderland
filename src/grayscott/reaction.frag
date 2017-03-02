# version 130

in vec2 uv_texcoord;

uniform float dx;
uniform float dy;

uniform float rU;
uniform float rV;

uniform float feed;
uniform float kill;

uniform sampler2D uv_texture;

out vec4 result;

void main()
{
    vec2 uv  = texture(uv_texture, uv_texcoord).rg;
    vec2 uv0 = texture(uv_texture, uv_texcoord + vec2(dx, 0.0)).rg;
    vec2 uv1 = texture(uv_texture, uv_texcoord + vec2(0.0, dy)).rg;
    vec2 uv2 = texture(uv_texture, uv_texcoord + vec2(-dx, 0.0)).rg;
    vec2 uv3 = texture(uv_texture, uv_texcoord + vec2(0.0, -dy)).rg;

    vec2 lapl = uv0 + uv1 + uv2 + uv3 - 4.0 * uv;
    float du = rU * lapl.r - uv.r * uv.g * uv.g + feed * (1.0 - uv.r);
    float dv = rV * lapl.g + uv.r * uv.g * uv.g - (feed + kill) * uv.g;
    vec2 dst = uv + vec2(du, dv);

    result = vec4(dst, 0.0, 1.0);
}
