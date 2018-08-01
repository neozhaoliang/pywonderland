// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com
/* ------------------------------------------ */

#version 3.7;

#include "default-settings.inc"

#macro choose_face(i, fase_size)
    #local chosen = false;
    #if ((face_size > 0.2 & face_size < 0.8) | (i=0 & face_size > 1))
        #local chosen = true;
    #end
    chosen
#end

camera {
    location <0, 1.25, 3> * 40
    look_at <0, 0, 0>
    angle 40
    up y*image_height
    right x*image_width
}

light_source {
    <0, 1, 1> * 100
    color rgb 1
}

#include "polychora-helpers.inc"

#macro Edge(i, p1, p2)
    #local q1 = proj4d(p1);
    #local q2 = proj4d(p2);
    cylinder {
        q1, q2, edge_size*(get_size(proj4d((p1+p2)/2)))
        edge_tex(i)
    }
#end

#macro FlatFace(i, num, pts, face_center, face_size)
    #local chosen = choose_face(i, face_size);
    #if (chosen)
        polygon {
            num+1,
            #local ind=0;
            #while (ind<num)
                proj4d(pts[ind])
                #local ind=ind+1;
            #end
            proj4d(pts[0])
            face_tex(i)
        }
    #end
#end

#macro BubbleFace(i, num, pts, sphere_center, sphere_radius, face_size)
    FlatFace(i, num, pts, sphere_center, face_size)
#end

union {
    #include "polychora-data.inc"
    scale 40 / extent
    rotate x*90
}
