// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

/*
===============================
Draw curved polychoron examples
===============================
*/

#version 3.7;

#include "colors.inc"
#include "textures.inc"
#include "mathutils.inc"
#include "polychora-data.inc"

global_settings {
  assumed_gamma 2.2
  max_trace_level 8
}

background { color bg_color }

#declare num_segments = 30;
#declare face_transmit = 0.7;
#declare nvertices = dimension_size(vertices, 1);

#macro Vertices(theta, phi, xi)
  #local out = array[nvertices];
  #for(i, 0, nvertices-1)
    #local out[i] = rotate4d(theta, phi, xi, vertices[i]);
  #end
  out
#end

#declare rvs = Vertices(2*clock*pi, 0, 2*clock*pi);

// project the arc between two 4d points on sphere S^3 to 3d
#macro get_arc(p1, p2)
  sphere_sweep {
    cubic_spline
    num_segments + 3,
    proj4d(p1), edge_size*get_size(proj4d(p1))
    #local ind=0;
    #while (ind < num_segments)
      #local q = proj4d(p1 + ind*(p2-p1)/num_segments);
      q, edge_size*get_size(q)
      #local ind = ind+1;
    #end
    proj4d(p2), edge_size*get_size(proj4d(p2))
    proj4d(p2), edge_size*get_size(proj4d(p2))
  }
#end

#declare edgeColors = array[4] { Silver, Brass, Firebrick, GreenCopper };
#declare faceColors = array[6] { White*0.9, Violet, Pink, Yellow, Brown, Magenta };

#declare vertexFinish = finish { ambient 0.5 diffuse 0.5 reflection 0.1 roughness 0.03 specular 0.5 }
#declare edgeFinish = finish { metallic ambient 0.2 diffuse 0.7 brilliance 6 reflection 0.25 phong 0.75 phong_size 80 }
#declare faceFinish = finish {
  ambient 0.5
  diffuse 0.5
  reflection 0.1
  specular 0.4
  roughness 0.003
  irid { 0.3 thickness 0.2 turbulence 0.05 }
  conserve_energy
}
#declare vertexTexture = texture { pigment { color Gold } finish { vertexFinish } }

#macro edgeTexture(i)
  texture {
    pigment { edgeColors[i] }
    finish { edgeFinish }
  }
#end

#macro faceTexture(i)
  texture {
    pigment {
      color faceColors[i]
      transmit face_transmit
    }
    finish { faceFinish }
  }
#end

#macro BubbleFace(faceType, nsides, pts)
  #local sphere_info = get_sphere_info(nsides, pts);
  #local isPlane = (sphere_info[2].x < 0);
  #local face_size = sphere_info[2].y;
  #local chosen = choose_face(faceType, face_size);
  #if (chosen)
    #if (isPlane)
      #local face_center = sphere_info[0];
      #local pdist = vlength(face_center);
      #local pnormal = vnormalize(face_center);
      plane {
        pnormal, pdist
        faceTexture(faceType)
        clipped_by {
          union {
            #local ind = 0;
            #while (ind < nsides)
              #local ind2 = ind + 1;
              #if (ind2 = nsides)
                #local ind2 = 0;
              #end
              get_arc(pts[ind], pts[ind2])
              #local ind = ind + 1;
            #end
          }
        }
      }
    #else
      #local face_center = sphere_info[1];
      #local sphere_center = sphere_info[0];
      #local sphere_rad = sphere_info[2].z;
      #local ind = 0;
      #local planes = array[nsides];
      #local pts3d = array[nsides];
      #local dists = array[nsides];
      #local sides = array[nsides];
      #while (ind < nsides)
        #local ind2 = ind + 1;
        #if (ind2 = nsides)
          #local ind2 = 0;
        #end
        #local planes[ind] = get_clipping_plane(pts[ind], pts[ind2]);
        #local pts3d[ind] = proj4d(pts[ind]);
        #local dists[ind] = distance_point_plane(0, pts3d[ind], planes[ind]);
        #local sides[ind] = on_same_side(face_center, pts3d[ind], planes[ind]);
        #if (sides[ind] != true)
          #local planes[ind] = -planes[ind];
        #end
        #local ind = ind+1;
      #end
      sphere {
        sphere_center, sphere_rad
        faceTexture(faceType)
        #local ind = 0;
        #while (ind < nsides)
          clipped_by { plane { -planes[ind], dists[ind] } }
          #local ind = ind+1;
        #end
      }
    #end
  #end
#end

union {
  #for (ind, 0, nvertices-1)
    #local q = proj4d(rvs[ind]);
    sphere {
      q, vertex_size*get_size(q)
      texture { vertexTexture }
    }
  #end

  #local edge_types = dimension_size(edges, 1);
  #for (i, 0, edge_types-1)
    #local edge_list = edges[i];
    #local nedges = dimension_size(edge_list, 1);
    #for (j, 0, nedges-1)
      #local v1 = edge_list[j][0];
      #local v2 = edge_list[j][1];
      object {
        get_arc(rvs[v1], rvs[v2])
        edgeTexture(i)
      }
    #end
  #end

  #local face_types = dimension_size(faces, 1);
  #for (i, 0, face_types-1)
    #local face_list = faces[i];
    #local nfaces = dimension_size(face_list, 1);
    #local nsides = dimension_size(face_list, 2);
    #for (j, 0, nfaces-1)
      #local points = array[nsides];
      #for (k, 0, nsides-1)
        #local points[k] = rvs[face_list[j][k]];
      #end
      BubbleFace(i, nsides, points)
    #end
  #end
  scale 20
  rotate obj_rotation
}

camera {
  location camera_loc
  look_at <0, 0, 0>
  angle 40
  right x*image_width/image_height
  up y
}

light_source {
  <-1, 1, 2> * 200
  color rgb 1
}

light_source {
  <1, 3, 1> * 200
  color rgb 1
}

#if (use_area_light)
  light_source {
    camera_loc * 0.25
    color rgb 1
    area_light
    x*5, y*5
    3, 3
    adaptive 1
    orient
    jitter
  }
#end
