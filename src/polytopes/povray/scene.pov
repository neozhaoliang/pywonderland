// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

#include "colors.inc"
#include "textures.inc" 


global_settings {
    assumed_gamma 2.2
}


background { color SkyBlue }


// adjust the vertex and edge radius here
#declare vRad = 0.040;
#declare eRad = 0.020;
#declare numSegments = 30;


#declare vertex_tex = texture {
    pigment{ Yellow }
    finish { ambient .5 diffuse .5 reflection .0 specular .5 roughness 0.1 }
}


#declare edge_tex = texture {
    pigment{ Orange }
    finish { ambient .5 diffuse .5 reflection .0 specular .5 roughness 0.1}
} 


#macro Proj(p)
    #local q = p / sqrt(p.x*p.x + p.y*p.y + p.z*p.z + p.t*p.t);
    <q.x, q.y, q.z> / (1.0 + q.t)
#end


#macro getSize(q)
    #local len = vlength(q);
    #if (len < 3.0)
        #local len = len * len / 3;
    #end
    len
#end


#macro Vertex(p)
    sphere {
        Proj(p), vRad*getSize(Proj(p))
        texture{ vertex_tex }
    }
#end


#macro Arc(p1, p2)
    sphere_sweep {
        cubic_spline
        numSegments + 3,
        Proj(p1), eRad*getSize(Proj(p1))
        #local i=0;
        #while (i < numSegments)
            #local q = Proj(p1 + i*(p2-p1)/numSegments);
            q, eRad*getSize(q)
            #local i=i+1;
        #end
        Proj(p2), eRad*getSize(Proj(p2))
        Proj(p2), eRad*getSize(Proj(p2))
        texture { edge_tex }
    }
#end


union {
    #include "polytope-data.inc"
    scale 8 
}


// adjust the camera position for rendering different polytopes
camera {
    location <0, 0, -130>
    look_at <0, -2, 0> 
    angle 40
    up y*image_height
    right x*image_width
}


light_source {
    <-1, 1, -1> * 150
    color rgb 1
}
 
