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

    for(int i=0; i<=3; ++i)
 
    {
        if (value > palette[i].a && value <= palette[i+1].a)
        {
            a = (value - palette[i].a) / (palette[i+1].a - palette[i].a);
            col = mix(palette[i].rgb, palette[i+1].rgb, a);
        }

    }

    if (value > palette[4].a)
    {
        col = palette[4].rgb;
    }

    finalColor = vec4(col.rgb, 1.0);
}
