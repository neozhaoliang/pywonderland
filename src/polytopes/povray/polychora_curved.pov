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
#include "math.inc"

global_settings {
    assumed_gamma 2.2
    max_trace_level 8
}

background { color White }

// number of spheres for sphere_sweep
#declare num_segments = 30;
#declare face_transmit = 0.7;

// stereographic project a 4d vector to 3d space
#macro proj4d(p)
    #local q = p / sqrt(p.x*p.x + p.y*p.y + p.z*p.z + p.t*p.t);
    <q.x, q.y, q.z> / (1.0 - q.t)
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

#declare edgeColors = array[4] { Silver, Brass, Firebrick, GreenCopper };
#declare faceColors = array[6] { White*0.9, Violet, Pink, Yellow, Brown, Magenta };

#declare vertexFinish = finish {
    ambient 0.5
    diffuse 0.5
    reflection 0.1
    roughness 0.03
    specular 0.5
}

#declare edgeFinish = finish {
    metallic
    ambient 0.2
    diffuse 0.7
    brilliance 6
    reflection 0.25
    phong 0.75
    phong_size 80
}

#declare vertexTexture = texture {
    pigment { color Gold }
    finish { vertexFinish }
}

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
        finish {
            ambient 0.5
            diffuse 0.5
            reflection 0.1
            specular 1
            roughness 0.005
            irid { 0.3 thickness 0.2 turbulence 0.05 }
            conserve_energy
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

#macro Edge(vs, i, v1, v2)
    object {
        get_arc(vs[v1], vs[v2])
        edgeTexture(i)
    }
#end

#macro FlatFace(i, num, pts, face_center, face_size)
    #local chosen = choose_face(i, face_size);
    #if (chosen)
        #local pdist = vlength(face_center);
        #local pnormal = vnormalize(face_center);
        plane {
            pnormal, pdist
            faceTexture(i)
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
    #end
#end

#macro BubbleFace(i, num, pts, sphere_center, sphere_radius, face_size)
    #local chosen = choose_face(i, face_size);
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
            faceTexture(i)
            #local ind = 0;
            #while (ind < num)
                clipped_by { plane { -planes[ind], dists[ind] } }
                #local ind = ind+1;
            #end
        }
    #end
#end

union {
    #include "polychora-data.inc"
    scale 40 / extent
    rotate object_rotation
}

camera {
    location camera_location
    look_at <0, 2, 0>
    angle 40
    right x*image_width/image_height
    up y
}

light_source {
    <-1, 1, 2> * 200
    color rgb 1
}
