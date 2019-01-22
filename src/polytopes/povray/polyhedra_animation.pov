// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/02/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

/*
=========================================
Make Animations of Rotating 3d Polyhedron
=========================================
*/

#version 3.7;

global_settings {
    assumed_gamma 2.2
}

#include "colors.inc"
#include "textures.inc"

background { White }

#declare vertexRad = 0.035;
#declare edgeRad = 0.02;

#declare vertexColor = SkyBlue;
#declare edgeColors = array[3]{ Orange, Pink,  SpringGreen };

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
    reflection 0.1
    specular 0.6
    roughness 0.005
}

#declare faceTextures = array[3]{
    texture {
        pigment { rgbf <0.4, 0.72, 0.4, 0.6> }
        finish { faceFinish }
    },

    texture {
        pigment { rgbf <0.9, 0.1, 0.2, 0.8> }
        finish { faceFinish }
    },

    texture {
        pigment { rgbf <0.1, 0.15, 0.5, 0.8> }
        finish { faceFinish }
    }
};

#macro Vert(vs, k)
    sphere {
        vs[k], vertexRad
        texture {
            pigment { color vertexColor }
            finish { edgeFinish }
        }
    }
#end

#macro Edge(vs, i, v1, v2)
    cylinder {
        vs[v1], vs[v2], edgeRad
        texture {
            pigment { color edgeColors[i] }
            finish { edgeFinish }
        }
    }
#end

#macro Face(vs, i, num, indices)
    #local center = 0;
    #for (ind, 0, num-1)
        #local center = center + vs[indices[ind]];
    #end
    #local center = center / num;

    union {
        polygon {
            num + 1,
            #for (ind, 0, num-1)
                vs[indices[ind]]
            #end
            vs[indices[0]]
        }
        plane {
            vnormalize(center), vlength(center)
            clipped_by {
                #for (ind, 0, num-1)
                    #local nv = vnormalize(vcross(vs[indices[ind]], vs[indices[mod(ind+1, num)]]));
                    #if (vdot(center - vs[indices[ind]], nv) > 0)
                        #local nv = -nv;
                    #end
                    plane {
                        nv, 0
                    }
                #end
            }
        }
        texture { faceTextures[i] }
    }
#end

union {
    #include "polyhedra-data.inc"
}

camera {
    location <0, 2, 1> * 1.5
    look_at <0, 0, 0>
    angle 40
    right x*image_width/image_height
    up y
    sky y
}

light_source {
    <1, 3, 1> * 100
    color rgb 0.9
}

light_source {
    <-2, 1, 1> * 100
    color rgb 0.8
}
