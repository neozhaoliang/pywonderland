# version 130

in vec2 Texcoord;

const int max_iter = 200;
const float radius = 100.0;

out vec4 result;

void main()
{
    int count = 0;
    vec2 p = vec2(-2.1 + 2.9 * Texcoord.x, -1.16 + 2.32 * Texcoord.y);
    vec2 z = vec2(0.0);

    for(int i=0; i< max_iter; i++)
    {
      z = vec2(z.x * z.x - z.y * z.y, 2 * z.x * z.y) + p;
      if (dot(z, z) > radius)
          break;
      count += 1;
    }
    if (count == max_iter)
    {
        result = vec4(0.0, 0.0, 0.0, 1.0);
    }
    else
    {
        float v = count + 1 - log2(log2(sqrt(dot(z, z))));
        v = log2(v) / 5.0;
        vec3 color = vec3(0.0);
        if (v < 1.0)
        {
            color = vec3(pow(v, 4), pow(v, 2.5), v);
        }
        else
        {
            v = max(0, 2.0 - v);
            color = vec3(v, pow(v, 1.5), pow(v, 3));
        }
        result = vec4(color, 1.0);
    }
}
