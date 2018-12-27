// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

#include "default-settings.inc"

#declare vertex_size = 0.03;
#declare edge_size = 0.015;

#declare face_transmit = 0.5;

#macro choose_face(i, face_size)
    #local chosen = false;
    #if ((i=0 & face_size > 0.6) | (i=2 & face_size > 0.2))
        #local chosen = true;
    #end
    chosen
#end

camera {
    location <0, 0, 1> * 130
    look_at <0, 0, 0>
    angle 40
    up y*image_height
    right x*image_width
}

light_source {
    <1, 1, 1> * 100
    color rgb 1
}

#include "polychora-helpers.inc"

union {
    #include "polychora-data.inc"
    scale 40 / extent
}
