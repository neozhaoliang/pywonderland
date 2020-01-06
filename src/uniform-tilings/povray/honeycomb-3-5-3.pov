/*
------------------------------------------------------
Main scene file for rendering 3D hyperbolic honeycombs 
------------------------------------------------------

This is the example scene for the regular 3-5-3 honeycomb

by Zhao Liang 2019/12/25

*/
#version 3.7;

#include "colors.inc"

global_settings {
    assumed_gamma 2.2
    max_trace_level 10
}

background { LightBlue }

// radius of a geodesic arc in hyperbolic metric
#declare hyper_radius = 0.035;
// number of spheres used in sphere_sweep
#declare num_segments = 20;

#declare edge_finish = finish {
  metallic
  ambient 0.3
  diffuse 0.7
  specular 0.5
  brilliance 6
  phong 0.6
  phong_size 70
  roughness 0.1
}

#declare vertex_color = MediumVioletRed;

#declare edge_tex = texture {
  pigment { MediumSeaGreen }
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
  #local cross = vlength(vcross(vnormalize(p1), vnormalize(p2)));
  // if p1 and p2 are colliner then connect them with
  // linearly interpolated spheres with constant hyperbolic radius
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
    // else we find the center and radius of the geodesic arc
    // connnets p1 and p2, this requires three different points
    // on the circle. Since we know this circle is orthogonal
    // to the unit ball hence the inversion of p1 (or p2) is also
    // on the circle and can be used as the third point.
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
        #local theta = acos(vdot(p1-center, p2-center) / (rad*rad));
        #local theta2 = k / num_segments * theta;
        #local ax = vcross(p1-center, p2-center);
        #local point = vaxis_rotate(p1-center, ax, theta2/pi*180) + center;
        point, get_hyperbolic_rad(point, hyper_radius)
      #end
      texture { edge_tex }
    }
  #end
#end

union {
  #include "honeycomb-data.inc"
  
  #for (k, 0, num_vertices-1)
    #local q = vertices[k];
    sphere {
      q, get_hyperbolic_rad(q, hyper_radius*3)
      texture{
        pigment{ color vertex_color }
        finish {
          edge_finish }
      }
    }
  #end

}

camera {
  location camera_loc
  look_at lookat
  up y
  right x*image_width/image_height
}

light_source {
  camera_loc
  color White
  area_light
  x*0.7, y*0.7,
  3, 3
  jitter
  adaptive 1
}

light_source {
  <0, 1, 0.5>
  color White*1.3
}
