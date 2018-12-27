// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

#include "default-settings.inc"

#declare vertex_size = 0.025;
#declare edge_size = 0.015;

camera {
    location <0, 0, 1> * 3.5
    look_at <0, 0, 0>
    angle 40
    up y*image_height
    right x*image_width
}

light_source {
    <0, 1, 2> * 100
    color rgb 1
}

light_source {
    <0, 1, 0> * 15
    color rgb 0.5
}

#include "polychora-helpers.inc"

union {
    #include "polychora-data.inc"
    rotate x*70
}
