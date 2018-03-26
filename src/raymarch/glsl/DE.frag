#version 130

int   MaxRaySteps = 256;
float minDist     = 0.0001;
float maxDist     = 1000.0;
float normalDist  = 0.0001;


// Return the normal vector at a point p,
// this requires the distance estimation function "DE" is implemented.
vec3 getNormal(vec3 p)
{
    vec3 epsilon = vec3(normalDist, 0.0, 0.0);
    return normalize(vec3(DE(p + epsilon.xyz) - DE(p - epsilon.xyz),
                          DE(p + epsilon.yxz) - DE(p - epsilon.yxz),
                          DE(p + epsilon.yzx) - DE(p - epsilon.yzx)));
}
