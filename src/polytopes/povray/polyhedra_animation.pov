// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/02/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

/*
=========================================
Make Animations of Rotating 3d Polyhedron
=========================================
*/

#version 3.7;

global_settings { assumed_gamma 2.2 }

#include "colors.inc"
#include "polytope-data.inc"

background { White }

#declare vertexRad = 0.035;
#declare edgeRad = 0.02;
#declare face_filter = 0.4;

#declare vertexColor = SkyBlue;
#declare edgeColors = array[3]{ Orange, GreenYellow, Maroon };
#declare faceColors = array[3]{ Pink, Violet, Brass };
#declare edgeFinish = finish { ambient 0.2 diffuse 0.5 reflection 0.1 specular 0.6 roughness 0.01 }
#declare faceFinish = finish { ambient 0.5 diffuse 0.5 specular 0.6 roughness 0.005 }

#macro faceTexture(i)
  texture {
    pigment { faceColors[i] filter face_filter }
    finish { faceFinish }
  }
#end

union {
  #local nvertices = dimension_size(vertices, 1);

  #for (ind, 0, nvertices-1)
    sphere {
      vertices[ind], vertexRad
      texture {
        pigment { color vertexColor }
        finish { edgeFinish }
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
        vertices[v1], vertices[v2], edgeRad
        texture {
          pigment { color edgeColors[i] }
          finish { edgeFinish }
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
      polygon {
        nsides + 1,
        #for (ind, 0, nsides-1)
          vertices[face_list[j][ind]]
        #end
        vertices[face_list[j][0]]
        faceTexture(i)
      }
    #end
  #end
  rotate <720*clock, 0, 360*clock>
}

camera {
  location <0, 0, 3.6>
  look_at <0, 0, 0>
  angle 40
  right x*image_width/image_height
  up y
  sky y
}

light_source {
  <1, 1, 3> * 100
  color rgb 1.3
}
