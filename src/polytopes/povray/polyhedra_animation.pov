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
#declare faceColors = array[3]{ Pink, DarkTurquoise, Brass };
#declare edgeFinish = finish { ambient 0.2 diffuse 0.5 reflection 0.1 specular 0.6 roughness 0.01 }
#declare faceFinish = finish { ambient 0.5 diffuse 0.5 specular 0.6 roughness 0.005 }

#macro faceTexture(i)
  texture {
    pigment { faceColors[i] filter face_filter }
    finish { faceFinish }
  }
#end

#macro getT(v1, v2, v3, v4)
  #local d1 = vnormalize(v2 - v1);
  #local d2 = vnormalize(v4 - v3);
  #local u1 = vcross(d1, d2);
  #if (vlength(u1) = 0)
    #local result = 0;
  #else
    #local u2 = vcross(v3- v1, d2);
    #local result = vdot(u2, u1) / vdot(u1, u1);
  #end
  result
#end

#macro isStar(v1, v2, v3, v4)
  #local result = false;
  #local tt = getT(v1, v2, v3, v4);
  #local ss = getT(v3, v4, v1, v2);
  #if ((tt > 0) & (tt < 1) & (ss > 0) & (ss < 1))
    #local result = true;
  #end
  result
#end

#macro getpoint(v1, v2, v3, v4)
  #local tt = getT(v1, v2, v3, v4);
  v1 + tt * vnormalize(v2 - v1);
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
    #if (nsides = 3)
      #for (j, 0, nfaces-1)
         polygon {
           4,
           #for (ind, 0, 2)
             vertices[face_list[j][ind]]
           #end
           vertices[face_list[j][0]]
           faceTexture(i)
         }
      #end
    #else
      #for (j, 0, nfaces-1)
        #local u1 = vertices[face_list[j][0]];
        #local u2 = vertices[face_list[j][1]];
        #local u3 = vertices[face_list[j][2]];
        #local u4 = vertices[face_list[j][3]];
        #if (isStar(u1, u2, u3, u4))
          #for (k, 0, nsides-1)
            #local v1 = vertices[face_list[j][mod(k, nsides)]];
            #local v2 = vertices[face_list[j][mod(k+1, nsides)]];
            #local v3 = vertices[face_list[j][mod(k+2, nsides)]];
            #local v4 = vertices[face_list[j][mod(k+3, nsides)]];
            #local p = getpoint(v1, v2, v3, v4);
            polygon {
              4
              p, v2, v3, p
              faceTexture(i)
            }
          #end
        #else
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
