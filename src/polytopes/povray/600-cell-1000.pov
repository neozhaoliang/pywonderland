// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

#include "default-settings.inc"

#declare vertex_size = 0.12;
#declare edge_size = 0.04;

#declare face_transmit = 0.5;

#macro get_size(q)
    #local len = vlength(q);
    #local len = 2.0 * log(1.13 + len * len);
    len
#end

#macro choose_face(i, fase_size)
    #local chosen = false;
    #if (face_size > 3.0 & face_size < 4.0)
        #local chosen = true;
    #end
    chosen
#end

camera {
    location <0, 0, 1> * 150
    look_at <0, 3, 0>
    angle 40
    up y*image_height
    right x*image_width
}

light_source {
    <0, 1, 2> * 200
    color rgb 1
}

light_source {
    <-1, 1, 0> * 200
    color rgb 1
}

#include "polychora-helpers.inc"

union {
    #include "polychora-data.inc"
    scale 40 / extent
}
