// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com
// This scene file is used for rendering the 3d polyhedron

#version 3.7;

#include "colors.inc"

global_settings {
    assumed_gamma 2.2
}

background { White }

#declare vRad = 0.035;  // vertex size
#declare eRad = 0.020;  // edge size
#declare faceFilter = 0.5;  // face transparent

#declare edge_finish = finish { specular 1 roughness 0.003 phong 0.9 phong_size 100 diffuse 0.7 reflection 0.1 }
#declare face_finish = finish { specular 0.4 diffuse 0.6 roughness 0.001 reflection 0.2 }
#declare vertex_tex = texture { pigment{ color rgb 0.05 } finish { edge_finish } }
#declare edge_colors = array[3] { Orange, Green, Red };
#declare face_colors = array[3] { Pink, Violet, Yellow };

#macro edge_tex(i)
    texture { pigment { edge_colors[i] } finish { edge_finish } }
#end

#macro face_tex(i)
    texture { pigment { face_colors[i] filter faceFilter } finish { face_finish } }
#end

#macro Vertex(p)
    sphere {
        p, vRad
        texture{ vertex_tex }
    }
#end

#macro Edge(i, p1, p2)
    cylinder {
        p1, p2, eRad
        edge_tex(i)
    }
#end

#macro Face(i, num, pts)
    polygon {
        num+1,
        #local ind=0;
        #while (ind<num)
            pts[ind]
            #local ind=ind+1;
        #end
        pts[0]
        face_tex(i)
    }
#end

union {
    #include "polyhedra-data.inc"
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
