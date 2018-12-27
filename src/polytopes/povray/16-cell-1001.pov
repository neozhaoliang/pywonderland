// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

#include "default-settings.inc"

#declare vertex_size = 0.1;
#declare edge_size = 0.04;

#macro choose_face(i, face_size)
    #local chosen = false;
    #if ((face_size < 1.2 & face_size > 0.3) | (i=2))
        #local chosen = true;
    #end
    chosen
#end

camera {
    location <0, 0, 1> * 200
    look_at <0, 3, 0>
    angle 40
    up y*image_height
    right x*image_width
}

light_source {
    <0, 1, 2> * 100
    color rgb 1
}

light_source {
    <-1, 1, 0> * 100
    color rgb 1
}

#include "polychora-helpers.inc"

union {
    #include "polychora-data.inc"
    scale 40 / extent
}
