#version 130

in  vec2 uv_texcoord;
out vec4 fragColor;

uniform sampler2D iChannel0;
uniform vec4      palette[5];

void main()
{
    float value = texture(iChannel0, uv_texcoord).y;
    float a;
    vec3 col;

    if (value <= palette[0].w)
    {
        col = palette[0].xyz;
    }

    for (int i=0; i<=3; ++i)

    {
        if (value > palette[i].w && value <= palette[i+1].w)
        {
            a = (value - palette[i].w) / (palette[i+1].w - palette[i].w);
            col = mix(palette[i].xyz, palette[i+1].xyz, a);
        }
    }
    fragColor = vec4(col.xyz, 1.0);
}
