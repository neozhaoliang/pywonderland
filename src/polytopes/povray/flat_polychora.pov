// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com
// This scene file is used for rendering "flat" 4d polytopes

#version 3.7;

#include "colors.inc"
#include "helpers.inc"

global_settings {
    assumed_gamma 2.2
}

background { color White }

#declare vRad = 0.06;
#declare eRad = 0.03;
#declare faceTransmit = 0.5;
#declare faceThreshold = 0.3;

#declare vert_finish = finish { specular 1 roughness 0.003 phong 0.9 phong_size 100 diffuse 0.7 reflection 0.1 }
#declare edge_finish = vert_finish;
#declare face_finish = finish { specular 0.4 diffuse 0.6 roughness 0.001 reflection 0.2 }
#declare vertex_tex = texture { pigment{ color rgb 0.05 } finish { vert_finish } }
#declare edge_colors = array[4] { Orange, Green, Red, Blue };
#declare face_colors = array[6] { Pink, Violet, Yellow, Maroon, Orchid, Brown }

#macro edge_tex(i)
    texture { pigment { edge_colors[i] } finish { edge_finish } }
#end

#macro face_tex(i)
    texture { pigment { face_colors[i] transmit faceTransmit } finish { face_finish } }
#end

#macro getSize(q)
    #local len = vlength(q);
    (1.0 + len * len) / 4
#end

#macro Vertex(p)
    #local q = vProj4d(p);
    sphere {
        q, vRad*getSize(q)
        texture{ vertex_tex }
    }
#end

#macro Edge(i, p1, p2)
    #local q1 = vProj4d(p1);
    #local q2 = vProj4d(p2);
    cylinder {
        q1, q2, eRad*getSize(vProj4d((p1+p2)/2))
        edge_tex(i)
    }
#end

#macro FlatFace(i, num, pts, faceSize, faceColor)
    #if (faceSize > faceThreshold)
        polygon {
          num+1,
            #local ind=0;
            #while (ind<num)
                vProj4d(pts[ind])
                #local ind=ind+1;
            #end
            vProj4d(pts[0])
            face_tex(i)
        }
    #end
#end

#macro BubbleFace(i, num, pts, sphereCenter, sphereRadius, faceSize, faceColor)
    FlatFace(i, num, pts, faceSize, faceColor)
#end

union {
    #include "polychora-data.inc"
    scale 1.0/extent
}

camera {
    location <0, 2, 1> * 1.5
    look_at <0, 0, 0>
    angle 40
    up y*image_height
    right x*image_width
}

light_source {
    <0, 3, 1> * 100
    color rgb 1
}
