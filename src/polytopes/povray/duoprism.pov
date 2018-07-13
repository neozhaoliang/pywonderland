// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com
/* ------------------------------------------
    Some params which you may need to adjust

1. vRad and eRad (control the vertex and radius size)
2. faceThreshold_0 and faceThreshold_1 (control which face to appear)
3. getSize fuction (you may use a self-defined one)
4. faceTransmit (control transparent of the face)
*/ 

#version 3.7;

#include "colors.inc"
#include "helpers.inc"

global_settings {
    assumed_gamma 2.2
}

background { color White }

#declare vRad = 0.06;
#declare eRad = 0.03;
#declare faceTransmit = 0.35;
#declare faceThreshold_0 = 1.0;
#declare faceThreshold_1 = 0.6;

#declare vert_finish = finish { specular 1 roughness 0.003 phong 0.9 phong_size 100 diffuse 0.7 reflection 0.1 }
#declare edge_finish = finish { specular 1 roughness 0.003 phong 0.9 phong_size 100 diffuse 0.7 reflection 0.1 }
#declare face_finish = finish { specular 0.1 diffuse 0.6 roughness 0.01 reflection 0.1 }
#declare vertex_tex  = texture { pigment{ color rgb 0.05 } finish { vert_finish } }
#declare edge_colors = array[2] { Orange, Cyan };
#declare face_colors = array[6] { Yellow, Maroon, Pink, Violet, Red, DustyRose }

#macro edge_tex(i)
    texture { pigment { edge_colors[i] } finish { edge_finish } }
#end

#macro face_tex(i)
    texture { pigment { face_colors[i] transmit faceTransmit } finish { face_finish } }
#end

#macro getSize(q)
    #local len = vlength(q);
    #local len = 1.5 * log((4.0 + len * len));
    len
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
        q1, q2, eRad*(getSize(vProj4d((p1+p2)/2)))
        edge_tex(i)
    }
#end

#macro FlatFace(i, num, pts, faceSize, faceColor)
    #if ((i=1 & faceSize < faceThreshold_1) | (i=0 & faceSize > faceThreshold_0))
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
    rotate x*90
}

camera {
    location <0, 1.25, 3>
    look_at <0, -0.1, 0>
    angle 40
    up y*image_height
    right x*image_width
}

light_source {
    <0, 1, 1> * 50
    color rgb 1
}
