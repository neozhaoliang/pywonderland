// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com
// This file is used for making gif animations of rotating 4d polychora


#version 3.7;

global_settings {
    assumed_gamma 2.2
    max_trace_level 8
} 

#default { finish { ambient 0.1 diffuse 0.9 phong 1 } }

#include "colors.inc"
#include "textures.inc"

background { Black }

#declare vertexRad = 0.02;
#declare edgeRad = 0.01;

#macro rotate4d(theta, phi, xi, vec)
    #local a = cos(xi);
    #local b = sin(theta)*cos(phi)*sin(xi);
    #local c = sin(theta)*sin(phi)*sin(xi);
    #local d = cos(theta)*sin(xi);
    #local p = vec.x;
    #local q = vec.y;
    #local r = vec.z;
    #local s = vec.t;
    < a*p - b*q - c*r - d*s
    , a*q + b*p + c*s - d*r
    , a*r - b*s + c*p + d*q
    , a*s + b*r - c*q + d*p >
#end

#macro proj3d(q)
    <q.x, q.y, q.z> / (2 - q.t) 
#end

#macro Vert(p, col)
    sphere {
        p, vertexRad
        texture {
            pigment { color col }
            finish {
                ambient 0.2
                diffuse 0.5
                reflection 0.1
                specular 3
                roughness 0.003 
            }
        }
    }
#end

#macro Edge(vs, i, j, col)
    cylinder { 
        vs[i], vs[j], edgeRad
        texture {
            pigment { color col }
            finish {
                ambient .5
                diffuse .5
                reflection .0
                specular .5
                roughness 0.1
            }
        
        }
    }
#end

#macro Face(vs, num, indices, faceTexture)
    polygon {
        num+1
        #for (ind, 0, num-1)
            vs[indices[ind]]
        #end
        vs[indices[0]]
        texture { faceTexture finish { reflection 0 } } 
    }
#end

union {
    #include "polychora-data.inc"
    #for(i, 0, nvertices-1)
        Vert(rvs[i], vertexColor)
    #end
    #for(i, 0, nedges-1)
        Edge(rvs, adjacencies[i][0], adjacencies[i][1], edgeColor)
    #end
    scale 4
}

camera {
    location <0, 0, -8>
    look_at 0
    right x*image_width/image_height
    angle 40
}

light_source {
    <100, 200, -500>
    color 0.9
}

light_source {
    <-100, 500, -200>
    color 0.9
}
