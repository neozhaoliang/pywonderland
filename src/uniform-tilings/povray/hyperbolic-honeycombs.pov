/*
------------------------------------------------------
Main scene file for rendering 3D hyperbolic honeycombs 
------------------------------------------------------

by Zhao Liang 2019/12/25

*/
#version 3.7;

#include "colors.inc"

global_settings {
    assumed_gamma 2.2
    max_trace_level 8
}

background { MidnightBlue }

// radius of a geodesic arc in hyperbolic metric
#declare hyper_radius = 0.09;
// number of spheres used in sphere_sweep
#declare num_segments = 50;

#declare edge_finish = finish {
  ambient 0.5
  diffuse 0.5
  reflection 0
  specular .5
  roughness 0.1
}

#declare edge_tex = texture {
  pigment { Silver }
  finish { edge_finish }
};

// hyperbolic distance to euclidean distance
#macro h2e(X)
    tanh(X/2)
#end

// euclidean distance to hyperbolic distance
#macro e2h(X)
    2*atanh(X)
#end

// get the euclidean radius of a sphere centered
// at a point p and has hyperbolic radius HR
#macro get_hyperbolic_rad(p, HR)
  #local R = vlength(p);
  #local r1 = h2e(e2h(R) + HR);
  #local r2 = h2e(e2h(R) - HR);
  (r1-r2)/2
#end

// inversion of a point p about the unit ball
#macro inversion(p)
  p / (p.x*p.x + p.y*p.y + p.z*p.z)
#end

// the hyperbolic geodesic arc connects two points p1, p2 in the
// unit ball, this arc has a constant hyperbolic radius hyper_radius
#macro HyperbolicEdge(p1, p2)
  #local cross = vlength(vcross(p1, p2));
  #if (cross < 1e-6)
    sphere_sweep {
      cubic_spline
      num_segments + 1
      #for (k, 0, num_segments)
        #local q1 = (p1 + k/num_segments * (p2 - p1));
        q1, get_hyperbolic_rad(q1, hyper_radius)
      #end
      texture { edge_tex }
    }
  #else
    #local p3 = inversion(p1);
    #local v1 = p2 - p1;
    #local v2 = p3 - p1;
    #local v11 = vdot(v1, v1);
    #local v22 = vdot(v2, v2);
    #local v12 = vdot(v1, v2);
    #local base = 0.5 / (v11 * v22 - v12 * v12);
    #local k1  = base * v22 * (v11 - v12);
    #local k2  = base * v11 * (v22 - v12);
    #local center = p1 + v1*k1 + v2*k2;
    #local rad = vlength(center - p1);
    sphere_sweep {
      cubic_spline
      num_segments + 1
      #for (k, 0, num_segments)
        #local q1 = (p1 + k/num_segments * (p2 - p1)) - center;
        #local q2 = vnormalize(q1) * rad + center;
        q2, get_hyperbolic_rad(q2, hyper_radius)
      #end
      tolerance 1e-2
      texture { edge_tex }
    }
  #end
#end

union {
  #include "honeycomb-data.inc"
  #for (k, 0, num_vertices-1)
    #local q = vertices[k];
    sphere {
      q, get_hyperbolic_rad(q, hyper_radius*2.5)
      texture{
        pigment{ color Orange }
        finish {
          ambient 0.5
          diffuse 0.5
          reflection 0.1
          roughness 0.03
          specular 0.5 }
      }
    }
  #end
}

camera {
  location <1, 1, 1> * 0.4
  look_at <1, 1.2, 1.2> * (-1)
  up z
  right x*image_width/image_height
}

light_source {
  <1, 1, 1> * 0.2
  color White
  area_light
  x, z
  5, 5
  adaptive 1
  jitter
}
