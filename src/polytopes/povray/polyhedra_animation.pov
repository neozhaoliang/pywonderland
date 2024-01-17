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

// set background color
background { White }

// size of vertices and edges
#declare vertexRad = 0.035;
#declare edgeRad = 0.02;

// set transparency of faces
#declare face_filter = 0.4;

#declare vertexColor = SkyBlue;
#declare edgeColors = array[3]{ Orange, GreenYellow, Maroon };
#declare faceColors = array[3]{ Pink, LightSteelBlue, Brass };
#declare edgeFinish = finish { ambient 0.2 diffuse 0.5 reflection 0.1 specular 0.6 roughness 0.01 }
#declare faceFinish = finish { ambient 0.5 diffuse 0.5 specular 0.6 roughness 0.005 }

// texture for the faces in the i-th orbit
#macro faceTexture(i)
  texture {
    pigment { faceColors[i] filter face_filter }
    finish { faceFinish }
  }
#end

// render the polytope
union {
  // get the number of vertices
  #local nvertices = dimension_size(vertices, 1);

  // render the vertives using spheres
  #for (ind, 0, nvertices-1)
    sphere {
      vertices[ind], vertexRad
      texture {
        pigment { color vertexColor }
        finish { edgeFinish }
      }
    }
  #end

  // get the number of orbits of edges
  #local edge_types = dimension_size(edges, 1);
  // for each orbit of edges
  #for (i, 0, edge_types-1)
    #local edge_list = edges[i];
    // get the number of edges in this orbit
    #local nedges = dimension_size(edge_list, 1);
    // render each edge by a cylinder connecting its two ends
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

  // get the number of orbits of faces
  #local face_types = dimension_size(faces, 1);
  #for (i, 0, face_types-1)
    #local face_list = faces[i];
    #local nfaces = dimension_size(face_list, 1);
    #local nsides = dimension_size(face_list, 2);
    #for (j, 0, nfaces-1)
      // if this face is a triangle
      #if (nsides = 3)
        triangle {
          vertices[face_list[j][0]],
          vertices[face_list[j][1]],
          vertices[face_list[j][2]]
          faceTexture(i)
        }
      // else use the union of successive triangles (center, v_{i}, v_{i+1})
      // to render this face, this works for both regular and star polygons.
      #else
        #local center = <0, 0, 0>;
        #for (k ,0, nsides-1)
          #local center = center + vertices[face_list[j][k]];
        #end
        #local center = center / nsides;
        #for (ind, 0, nsides-1)
          triangle {
            center,
            vertices[face_list[j][ind]],
            vertices[face_list[j][mod(ind+1, nsides)]]
            faceTexture(i)
          }
        #end
      #end
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
