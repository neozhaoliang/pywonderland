// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

/*
============================================================
Some math helper functions for rendering curved 4d polytopes
============================================================
*/
#include "math.inc"

// Rotate a 4d vector
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

// stereographic project a 4d vector to 3d space
#macro proj4d(p)
  #local q = p / sqrt(p.x*p.x + p.y*p.y + p.z*p.z + p.t*p.t);
  <q.x, q.y, q.z> / (1.0 + 1e-8 - q.t)
#end

// return the normal vector of a 3d plane passes through the
// projected points of two 4d vectors p1 and p2
#macro get_clipping_plane(p1, p2)
  #local q1 = proj4d(p1);
  #local q2 = proj4d(p2);
  #local q12 = proj4d((p1+p2)/2);
  VPerp_To_Plane(q1-q12, q2-q12)
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

#macro get_sphere_info(nsides, pts)
  #local result = array[3];
  #local A = proj4d(pts[0]);
  #local B = proj4d(pts[1]);
  #local C = proj4d(pts[2]);
  #local P = 0;
  #for (i, 0, nsides-1)
    #local P = P + pts[i];
  #end
  #local P = proj4d(P);
  #local p1 = A - P;
  #local p2 = B - P;
  #local p3 = C - P;
  #local det = p1.x * (p2.y*p3.z - p2.z*p3.y) -
               p1.y * (p2.x*p3.z - p2.z*p3.x) +
               p1.z * (p2.x*p3.y - p2.y*p3.x);
  #local det = det * 2;
  #if (abs(det) < 0.001)
    #local result = array[3] { P, P, <-1, vlength(p1), 0> };
  #else
    #local v1 = vcross(p1, p2) * vdot(p3, p3);
    #local v2 = vcross(p3, p1) * vdot(p2, p2);
    #local v3 = vcross(p2, p3) * vdot(p1, p1);
    #local cen = (v1 + v2 + v3) / det;
    #local sphere_rad = vlength(cen);
    #local sphere_center = P + cen;
    #local result = array[3] { sphere_center, P, <1, vlength(p1), sphere_rad> };
  #end
  result
#end
