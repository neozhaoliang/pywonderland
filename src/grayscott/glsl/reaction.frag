#version 130

in vec2 uv_texcoord;

uniform vec2      u_resolution;
uniform vec2      u_mouse;
uniform sampler2D uv_texture;
uniform sampler2D mask_texture;
uniform vec4      params;

out vec4 result;

void main()
{
    if(u_mouse.x < -5.0)
    {
        result = vec4(1.0, 0.0, 0.0, 1.0);
        return;
    }

    vec2 pixelSize = 1.0 / u_resolution;
    vec2 cen = texture(uv_texture, uv_texcoord).xy;
    vec2 rig = texture(uv_texture, uv_texcoord + vec2( pixelSize.x,          0.0)).xy;
    vec2 top = texture(uv_texture, uv_texcoord + vec2(         0.0,  pixelSize.y)).xy;
    vec2 lef = texture(uv_texture, uv_texcoord + vec2(-pixelSize.x,          0.0)).xy;
    vec2 bot = texture(uv_texture, uv_texcoord + vec2(         0.0, -pixelSize.y)).xy;

    float Du   = params.x;
    float Dv   = params.y;
    float feed = params.z * texture(mask_texture, uv_texcoord).x;
    float kill = params.w;

    vec2 lapl = rig + top + lef + bot - 4.0 * cen;
    float du = Du * lapl.x - cen.x * cen.y * cen.y + feed * (1.0 - cen.x);
    float dv = Dv * lapl.y + cen.x * cen.y * cen.y - (feed + kill) * cen.y;
    vec2 newValue = cen + 0.6 * vec2(du, dv);

    if(u_mouse.x > 0.0)
    {
        vec2 diff = (uv_texcoord - u_mouse) * u_resolution;
        float dist = dot(diff, diff);
        if(dist < 1.0)
            newValue.y = 0.9;
    }

    result = vec4(newValue, 0.0, 1.0);
}
