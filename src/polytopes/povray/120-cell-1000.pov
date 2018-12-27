// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

#include "default-settings.inc"

#declare face_transmit = 0.6;

#macro get_size(q)
    #local len = vlength(q);
    #local len = (1.0 + len * len) / 4;
    len
#end

#macro choose_face(i, face_size)
    #local chosen = false;
    #if ((face_size > 3.0))
        #local chosen = true;
    #end
    chosen
#end

camera {
    location <0, 0, 1> * 150
    look_at <0, 2, 0>
    angle 40
    up y*image_height
    right x*image_width
}

light_source {
    <-1, 1, 2> * 200
    color rgb 1
}

#include "polychora-helpers.inc"

union {
    #include "polychora-data.inc"
    scale 40 / extent
}
