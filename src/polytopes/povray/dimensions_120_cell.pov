// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com
// This scene file is used for recreating the scene in the dimensions movie

#version 3.7;

#include "colors.inc"
#include "helpers.inc"

global_settings {
    assumed_gamma 2.2
}

background { color SkyBlue }

#declare vRad = 0.05;
#declare eRad = 0.025;
#declare numSegments = 30;
#declare faceThreshold = 3.0;

#declare edge_finish = finish { ambient .5 diffuse .5 reflection .0 specular .5 roughness 0.1 }
#declare face_finish = finish { diffuse 0.8 specular 0.3 reflection 0.2 roughness 0.1 }
#declare vert_tex = texture { pigment { Yellow } finish { edge_finish } }
#declare edge_tex = texture { pigment { Orange } finish { edge_finish } }

#macro getSize(q)
    #local len = vlength(q);
    (1.0 + len * len) / 4
#end

#macro Vertex(p)
    #local q = vProj4d(p);
    sphere {
        q, vRad*getSize(q)
        texture{ vert_tex }
    }
#end

#macro Edge(i, p1, p2)
    sphere_sweep {
        cubic_spline
        numSegments + 3,
        vProj4d(p1), eRad*getSize(vProj4d(p1))
        #local i=0;
        #while (i < numSegments)
            #local q = vProj4d(p1 + i*(p2-p1)/numSegments);
            q, eRad*getSize(q)
            #local i=i+1;
        #end
        vProj4d(p2), eRad*getSize(vProj4d(p2))
        vProj4d(p2), eRad*getSize(vProj4d(p2))
        texture { edge_tex }
    }
#end

#macro FlatFace(i, num, pts, faceSize, faceColor)
    #if (faceSize > faceThreshold)
        polygon {
            num+1,
            #local ind=0;
            #while (ind<num)
                vProj4d(pts[ind])
                #local ind=ind+1;
            #end
            vProj4d(pts[0])
            pigment { rgb faceColor transmit 0.5 }
            finish { face_finish }
        }
    #end
#end

#macro BubbleFace(i, num, pts, sphereCenter, sphereRadius, faceSize, faceColor)
    #if (faceSize > faceThreshold)
        #local rib = 0;
        #local ind = 0;
        #while (ind < num)
            #local rib = rib + pts[ind];
            #local ind = ind+1;
        #end
        #local rib3d = vProj4d(rib);

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
            #local planes[ind] = getClippingPlane(pts[ind], pts[ind2]);
            #local pts3d[ind] = vProj4d(pts[ind]);
            #local dists[ind] = distancePointPlane(0, pts3d[ind], planes[ind]);
            #local sides[ind] = onSameSide(rib3d, pts3d[ind], planes[ind]);
            #if (sides[ind] != true)
                #local planes[ind] = -planes[ind];
            #end
            #local ind = ind+1;
        #end

        #local col = vnormalize(rib3d);
        sphere {
            sphereCenter, sphereRadius
            pigment { rgb faceColor transmit 0.5 }
            finish { face_finish }
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
    scale 1.0/extent * 40
}

camera {
    location <0, 0, 1> * 160
    look_at <0, 0, 0>
    angle 40
    up y*image_height
    right x*image_width
}

light_source {
    <0, 3, 1> * 100
    color rgb 1
}
