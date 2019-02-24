float dihedral(vec3 n1, vec3 n2)
{
    return PI - acos(dot(n1, n2));
}


float DE(vec3 p)
{
    return 0.0;
}


void main()
{
    FinalColor = vec4(1.0, 0.0, 1.0, 0.0);
}
