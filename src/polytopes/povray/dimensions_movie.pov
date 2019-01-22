// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

/*
=======================================================
Make Animation of the 120-cell in the movie "Dimensions"
=======================================================
*/

#version 3.7;

#include "colors.inc"
#include "math.inc"

global_settings {
    assumed_gamma 2.2
    max_trace_level 8
}

background { color SkyBlue }

// number of spheres for sphere_sweep
#declare num_segments = 30;

#declare vertex_size = 0.04;
#declare edge_size = 0.02;
#declare face_transmit = 0.6;
#declare face_index = 0;

// stereographic project a 4d vector to 3d space
#macro proj4d(p)
    #local q = p / sqrt(p.x*p.x + p.y*p.y + p.z*p.z + p.t*p.t);
    <q.x, q.y, q.z> / (1.0 - q.t)
#end

// adjust the size of vertices/edges by there positions
#macro get_size(q)
    #local len = vlength(q);
    #local len = (1.0 + len * len) / 4;
    len
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
            #local ind=ind+1;
        #end
        proj4d(p2), edge_size*get_size(proj4d(p2))
        proj4d(p2), edge_size*get_size(proj4d(p2))
     }
#end

#declare faceColors = array[12] {
    Pink,
    Green,
    Blue,
    Red,
    Orange,
    Yellow,
    Magenta,
    Gold,
    Cyan,
    Violet,
    Brass,
    Maroon
}

#declare Fin = finish {
    ambient .5
    diffuse .5
    reflection .0
    specular .5
    roughness 0.1
}

#declare vertexTexture = texture {
    pigment { Yellow }
    finish { Fin }
}

#declare edgeTexture = texture {
    pigment { Orange }
    finish { Fin }
}

#macro choose_face(face_size)
    #local chosen = false;
    #if ((face_size > 3.0))
        #local chosen = true;
    #end
    chosen
#end

#macro faceTexture(k)
    texture {
        pigment {
            color faceColors[k]
            transmit face_transmit
        }
        finish {
            ambient 0.5
            diffuse 0.5
            reflection 0.1
            specular 0.6
            roughness 0.005
        }
    }
#end

#macro Vert(vs, k)
    #local q = proj4d(vs[k]);
    sphere {
        q, vertex_size*get_size(q)
        texture { vertexTexture }
    }
#end

#macro Edge(vs, v1, v2)
    object {
        get_arc(vs[v1], vs[v2])
        texture { edgeTexture }
    }
#end

#macro FlatFace(i, num, pts, face_center, face_size)
    #local chosen = choose_face(face_size);
    #if (chosen)
        #local pdist = vlength(face_center);
        #local pnormal = vnormalize(face_center);
        plane {
            pnormal, pdist
            faceTexture(face_index)
            clipped_by {
                union {
                    #local ind = 0;
                    #while (ind < num)
                        #local ind2 = ind + 1;
                        #if (ind2 = num)
                            #local ind2 = 0;
                        #end
                        get_arc(pts[ind], pts[ind2])
                        #local ind = ind + 1;
                    #end
                }
            }
        }
        #declare face_index = face_index + 1;
    #end
#end

#macro BubbleFace(i, num, pts, sphere_center, sphere_radius, face_size)
    #local chosen = choose_face(face_size);
    #if (chosen)
        #local rib = 0;
        #local ind = 0;
        #while (ind < num)
            #local rib = rib + pts[ind];
            #local ind = ind+1;
        #end
        #local rib3d = proj4d(rib);

        #local ind = 0;
        #local planes = array[num];
        #local pts3d = array[num];
        #local dists = array[num];
        #local sides = array[num];
        #while (ind < num)
            #local ind2 = ind + 1;
            #if (ind2 = num)
                #local ind2 = 0;
            #end
            #local planes[ind] = get_clipping_plane(pts[ind], pts[ind2]);
            #local pts3d[ind] = proj4d(pts[ind]);
            #local dists[ind] = distance_point_plane(0, pts3d[ind], planes[ind]);
            #local sides[ind] = on_same_side(rib3d, pts3d[ind], planes[ind]);
            #if (sides[ind] != true)
                #local planes[ind] = -planes[ind];
            #end
            #local ind = ind+1;
        #end

        sphere {
            sphere_center, sphere_radius
            faceTexture(face_index)
            #local ind = 0;
            #while (ind < num)
                clipped_by { plane { -planes[ind], dists[ind] } }
                #local ind = ind+1;
            #end
        }
        #declare face_index = face_index + 1;
    #end
#end

camera {
    location <0, 0, 1> * 180
    look_at <0, 2, 0>
    angle 40
    up y*image_height
    right x*image_width
}

light_source {
    <-1, 2, 2> * 200
    color rgb 1
}

// This light is added when the camera is inside the 120-cell,
// which ranges from the 547-938 frames in our default settings.
#macro add_light(time)
    #if(time > 547/1199.0 & time < 938/1199.0)
        light_source {
            <0, 0, 180>
            color rgb 0.5
        }
    #end
#end

add_light(clock)

union {
    #include "120-cell-data.inc"
    scale 40 / extent
    rotate <0, 720*clock, 0>
    #if (clock < 0.5)
        translate <0, 0, 300*clock>
    #else #if (clock < 0.75)
        translate <0, 0, 150>
    #else
        translate <0, 0, 150-(clock-0.75)*480>
    #end
    #end
}
