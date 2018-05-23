// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com
// Some params you need to adjust when rendering different polytopes:
// 1. the camera position
// 2. the vertex and edge radius
// 3. the face threshould (controls which faces are shown)
// 4. the getSize function (controls the gradient change of the edge)

#version 3.7;

#include "colors.inc"
#include "helpers.inc"

global_settings {
    assumed_gamma 2.2
}

background { color SkyBlue }

// adjust the vertex and edge radius here
#declare vRad = 0.040;
#declare eRad = 0.020;
#declare numSegments = 30;
#declare faceThreshould = 3.0;

#declare vertex_tex = texture {
    pigment{ Yellow }
    finish { ambient .5 diffuse .5 reflection .0 specular .5 roughness 0.1 }
}

#declare edge_tex = texture {
    pigment{ Orange }
    finish { ambient .5 diffuse .5 reflection .0 specular .5 roughness 0.1}
}

#declare face_fin = finish { diffuse 0.8 specular 0.3 reflection 0.2 roughness 0.1 }


#macro getSize(q)
    #local len = vlength(q);
    (1.0 + len * len) / 4
#end


#macro Vertex(p)
    #local q = vProj4d(p);
    sphere {
        q, vRad*getSize(q)
        texture{ vertex_tex }
    }
#end


#macro Arc(p1, p2)
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


#macro FlatFace(num, pts, faceSize, faceColor)
    #if (faceSize > faceThreshould)
        polygon {
            num+1,
            #local i=0;
            #while (i<num)
                vProj4d(pts[i])
                #local i=i+1;
            #end
            vProj4d(pts[0])

            pigment { rgbt <faceColor.x, faceColor.y, faceColor.z, 0.5> }
            finish { face_fin }
        }
    #end
#end


#macro BubbleFace(num, pts, sphereCenter, sphereRadius, faceSize, faceColor)
    #if (faceSize > faceThreshould)
        #local rib = 0;
        #local i = 0;
        #while (i < num)
            #local rib = rib + pts[i];
            #local i = i+1;
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
            pigment { rgbt <faceColor.x, faceColor.y, faceColor.z, 0.5> }
            finish { face_fin }
            #local i = 0;
            #while (i < num)
                clipped_by { plane { -planes[i], dists[i] } }
                #local i = i+1;
            #end
        }
    #end
#end


union {
    #include "polytope-data.inc"
    scale 8
}


// adjust the camera position for rendering different polytopes
camera {
    location <0, 0, 1> * (-160)
    look_at <0, 2, 0>
    angle 40
    up y*image_height
    right x*image_width
}


light_source {
    <-1, 1, -1> * 150
    color rgb 1
}
