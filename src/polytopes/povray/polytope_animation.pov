// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2019/01/04
// Auth: Zhao Liang mathzhaoliang@gmail.com

/*
========================================
Make Animations of Rotating 4d Polytopes
========================================
*/

#version 3.7;

global_settings {
  assumed_gamma 2.2
  max_trace_level 8
}

#include "colors.inc"
#include "textures.inc"
#include "polytope-data.inc"

background { Black }

#declare vertexRad = 0.02;
#declare edgeRad = 0.01;
#declare nvertices = dimension_size(vertices, 1);

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

#macro Vertices(theta, phi, xi)
  #local out = array[nvertices];
  #for(i, 0, nvertices-1)
    #local out[i] = proj3d(rotate4d(theta, phi, xi, vertices[i]));
  #end
  out
#end

#declare rvs = Vertices(2*clock*pi, 0, 2*clock*pi);

union {
  #for (ind, 0, nvertices-1)
    sphere {
      rvs[ind], vertexRad
      texture {
        pigment { color SkyBlue }
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

  #local edge_types = dimension_size(edges, 1);
  #for (i, 0, edge_types-1)
    #local edge_list = edges[i];
    #local nedges = dimension_size(edge_list, 1);
    #for (j, 0, nedges-1)
      #local v1 = edge_list[j][0];
      #local v2 = edge_list[j][1];
      cylinder {
        rvs[v1], rvs[v2], edgeRad
        texture {
          pigment { color Orange }
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
  #end

  #local face_types = dimension_size(faces, 1);
  #for (i, 0, face_types-1)
    #local face_list = faces[i];
    #local nfaces = dimension_size(face_list, 1);
    #local nsides = dimension_size(face_list, 2);
    #for (j, 0, nfaces-1)
      #if (nsides = 3)
        triangle {
          rvs[face_list[j][0]],
          rvs[face_list[j][1]],
          rvs[face_list[j][2]]
          texture { NBglass finish { reflection 0 }}
        }
      #else
        #local center = <0, 0, 0>;
        #for (k ,0, nsides-1)
          #local center = center + rvs[face_list[j][k]];
        #end
        #local center = center / nsides;
        #for (ind, 0, nsides-1)
          triangle {
            center,
            rvs[face_list[j][ind]],
            rvs[face_list[j][mod(ind+1, nsides)]]
            texture { NBglass finish { reflection 0 }}
          }
        #end
      #end
    #end
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
  <500, 500, -1000>
  color 1.3
}
