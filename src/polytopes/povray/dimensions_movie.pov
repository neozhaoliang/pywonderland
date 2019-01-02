// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

#include "colors.inc"

global_settings {
    assumed_gamma 2.2
    max_trace_level 10
}

background { color SkyBlue }

#declare vertex_size = 0.04;
#declare edge_size = 0.02;
#declare face_transmit = 0.6;

#declare face_colors = array[12] {
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

#declare face_index = 0;

#declare Fin = finish {
    ambient .5
    diffuse .5
    reflection .0
    specular .5
    roughness 0.1
}

#declare vertex_tex = texture {
    pigment { Yellow }
    finish { Fin }
}

#declare edge_tex = texture {
    pigment { Orange }
    finish { Fin }
}

#macro get_size(q)
    #local len = vlength(q);
    #local len = (1.0 + len * len) / 4;
    len
#end

#macro choose_face(i, face_size)
    #local chosen = false;
    #if ((face_size > 3.0))
        #local chosen = true;
    #end
    chosen
#end

#macro face_tex(k)
    texture {
        pigment {
            color face_colors[k]
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

#include "polychora-helpers.inc"

#macro Vertex(p)
    #local q = proj4d(p);
    sphere {
        q, vertex_size*get_size(q)
        texture { vertex_tex }
    }
#end

#macro Edge(i, p1, p2)
    object {
        get_arc(p1, p2)
        texture { edge_tex }
    }
#end

#macro FlatFace(i, num, pts, face_center, face_size)
    #local chosen = choose_face(i, face_size);
    #if (chosen)
        #local pdist = vlength(face_center);
        #local pnormal = vnormalize(face_center);
        plane {
            pnormal, pdist
            face_tex(face_index)
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
            face_tex(face_index)
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
            color rgb 1
        }
    #end
#end

add_light(clock)

union {
    #include "polychora-data.inc"
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
