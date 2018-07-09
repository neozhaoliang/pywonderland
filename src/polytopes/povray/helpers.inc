// Persistence of Vision Ray Tracer Include File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

#include "math.inc"

// stereographic project a 4d vector to 3d space
#macro vProj4d(p)
    #local q = p / sqrt(p.x*p.x + p.y*p.y + p.z*p.z + p.t*p.t);
    <q.x, q.y, q.z> / (1.0 - q.t)
#end

// return the normal vector of a 3d plane passes through the
// projected points of two 4d vectors p1 and p2
#macro getClippingPlane(p1, p2)
    #local q1 = vProj4d(p1);
    #local q2 = vProj4d(p2);
    #local q12 = vProj4d((p1+p2)/2);
    VPerp_To_Plane(q1-q12, q2-q12)
#end

// compute the signed distance of a vector to a plane,
// all vectors here are in 3d.
#macro distancePointPlane(p, p0, pnormal)
    vdot(p-p0, pnormal) / vlength(pnormal)
#end

// check if a vectors p is in the halfspace defined
// by the plane passes through p0 and has orientation pNormal.
#macro onSameSide(p, p0, pNormal)
    #local result = false;
    #local innprod = vdot(pNormal, p-p0);
    #if (innprod > 0)
        #local result = true;
    #end
    result
#end
