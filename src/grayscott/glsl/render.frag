#version 130

in vec2 uv_texcoord;

uniform sampler2D uv_texture;
uniform vec4 palette[5];

out vec4 finalColor;

void main()
{
    float value = texture(uv_texture, uv_texcoord).g;
    float a;
    vec3 col;

    if (value <= palette[0].a)
    {
        col = palette[0].rgb;
    }

    if (value > palette[0].a && value <= palette[1].a)
    {
        a = (value - palette[0].a) / (palette[1].a - palette[0].a);
        col = mix(palette[0].rgb, palette[1].rgb, a);
    }

    if (value > palette[1].a && value <= palette[2].a)
    {
        a = (value - palette[1].a) / (palette[2].a - palette[1].a);
        col = mix(palette[1].rgb, palette[2].rgb, a);
    }

    if (value > palette[2].a && value <= palette[3].a)
    {
        a = (value - palette[2].a) / (palette[3].a - palette[2].a);
        col = mix(palette[2].rgb, palette[3].rgb, a);
    }

    if (value > palette[3].a && value <= palette[4].a)
    {
        a = (value - palette[3].a) / (palette[4].a - palette[3].a);
        col = mix(palette[3].rgb, palette[4].rgb, a);
    }

    if (value > palette[4].a)
    {
        col = palette[4].rgb;
    }

    finalColor = vec4(col.rgb, 1.0);
}
