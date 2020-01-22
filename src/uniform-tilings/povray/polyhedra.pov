/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
3D Spherical tiling example scene file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

#version 3.7;

global_settings {
  assumed_gamma 1.0
}

#include "colors.inc"
#include "math.inc"

background { White }

#declare vertexRad = 0.035;
#declare edgeRad = 0.02;
#declare edgeRad2 = 0.002;
#declare num_segments = 20;

#declare vertexColors = array[3] { SkyBlue, Silver, Magenta };
#declare edgeColors = array[3]{ Orange, GreenYellow, Maroon };
#declare faceColors = array[3] { Brass, MediumSeaGreen, Violet };
#declare faceColorsDimmed = array[3] { Brass*0.5, MediumSeaGreen*0.5, Violet*0.5 };

#declare edgeFinish = finish {
    ambient 0.2
    diffuse 0.5
    reflection 0.1
    specular 0.6
    roughness 0.01
}

#declare faceFinish = finish {
    ambient 0.5
    diffuse 0.5
    specular 0.6
    roughness 0.005
}

#macro faceTexture(ind, faceType)
  #if(faceType)
    #local col = faceColors[ind];
  #else
    #local col = faceColorsDimmed[ind];
  #end

  texture {
    pigment { col filter 0 }
    finish { faceFinish }
  }
#end

// return the normal vector of a 3d plane passes through the
// projected points of two 4d vectors p1 and p2
#macro get_clipping_plane(p1, p2)
    #local p12 = vnormalize(p1+p2);
    VPerp_To_Plane(p1-p12, p2-p12)
#end

// compute the signed distance of a vector to a plane,
// all vectors here are in 3d.
#macro distance_point_plane(p, p0, pnormal)
    vdot(p-p0, pnormal) / vlength(pnormal)
#end

// check if a vectors p is in the halfspace defined
// by the plane passes through p0 and has orientation pNormal.
#macro on_same_side(p, p0, pnormal)
    #local result = false;
    #local innprod = vdot(pnormal, p-p0);
    #if (innprod > 0)
        #local result = true;
    #end
    result
#end

#macro get_arc(p, q, arc_size)
  sphere_sweep {
    cubic_spline
    num_segments + 3
    p, arc_size
    #for (ind, 0, num_segments)
      #local point = p + (q - p) * ind / num_segments;
      #local point = vnormalize(point);
      point, arc_size
    #end
    q, arc_size
  }
#end

#macro Edge(k, i1, i2)
  #local p = vertices[i1];
  #local q = vertices[i2];
  object {
    get_arc(p, q, edgeRad)
    texture {
      pigment { edgeColors[k] }
      finish { edgeFinish }
    }
  }
#end


#macro Face(k, faceType, pts)
  union {
    #local num = dimension_size(pts, 1);
    #local rib = 0;
    #local ind = 0;
    #while (ind < num)
      #local rib = rib + pts[ind];
      #local ind = ind+1;
    #end
    #local rib = vnormalize(rib);
  
    #local ind = 0;
    #local planes = array[num];
    #local dists = array[num];
    #local sides = array[num];
    #while (ind < num)
      #local ind2 = ind + 1;
      #if (ind2 = num)
        #local ind2 = 0;
      #end
      #local planes[ind] = get_clipping_plane(pts[ind], pts[ind2]);
      #local dists[ind] = distance_point_plane(0, pts[ind], planes[ind]);
      #local sides[ind] = on_same_side(rib, pts[ind], planes[ind]);
      #if (sides[ind] != true)
        #local planes[ind] = -planes[ind];
      #end
      #local ind = ind+1;
    #end
    
    #if(num = 3)
      #local p1 = pts[0];
      #local p2 = pts[1];
      #local cen = pts[2];
      merge {
        get_arc(p1, cen, edgeRad2)
        get_arc(p2, cen, edgeRad2)
        no_shadow
        texture { pigment { Silver } finish { edgeFinish }}
      }
    #else
      #local p1 = pts[0];
      #local p2 = pts[2];
      #local cen = pts[3];
      merge {
        get_arc(p1, cen, edgeRad2)
        get_arc(p2, cen, edgeRad2)
        no_shadow
        texture { pigment { Silver } finish { edgeFinish }}
      }
    #end

    sphere {
      0, 1
      faceTexture(k, faceType)
      #local ind = 0;
      #while (ind < num)
        clipped_by { plane { -planes[ind], dists[ind] } }
        #local ind = ind+1;
      #end
    }
  }
#end
    
camera {
  location <0, 0, 2.5>
  look_at <0, 0, 0>
  up y
  right x*image_width/image_height
}

light_source {
  <10, 10, 3>
  color rgb 1
}

union {
  #include "polyhedra-data.inc"
  #for(ind, 0, num_vertices-1)
    sphere {
      vertices[ind], vertexRad
      texture {
        pigment { color SkyBlue }
        finish { edgeFinish }
      }
    }
  #end
}
