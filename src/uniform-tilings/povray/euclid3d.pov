#version 3.7;

global_settings {
    assumed_gamma 2.2
    max_trace_level 8
}

#include "colors.inc"
#include "textures.inc"

#declare RR = seed(314);

background { Black }

#declare colors = array[4] { Silver, Brass, Gold, SteelBlue };

#declare edgeFinish = finish {
    metallic
    ambient 0.5
    diffuse 0.5
    brilliance 6
    reflection 0
    specular 0.1
}

#declare AgateFn =
    function {
        pattern {
            agate
            turbulence 0.4
            omega 0.9
            octaves 2
            scale <1, 1, 1>/4
        }
    }

#macro Vert(k)
    sphere {
        vertices[k], 0.06
        pigment { color Orange }
        finish {
            metallic
            ambient 0.5
            diffuse 0.5
            brilliance 6
            reflection 0
            specular 0.1
        }
    }
#end

#macro Edge(vertices, ind, v1, v2)
    cylinder{
        vertices[v1], vertices[v2], 0.03
            texture {
                pigment {
                    function { AgateFn(x, y, z) }
                    color_map {
                        [ 0 rgb <0.40, 0.40, 0.41>*2.0 ]
                        [ 1 rgb <0.47, 0.50, 0.43>*1.2 ]
                    }
                }
                finish { ambient 0.1 diffuse 0.6 }
            }
    }
#end

union{
    #include "affine-data.inc"
}

camera {
    location <4.3, 8.5, 4.3> * 0.9
    look_at <-4.0, -8.5, -4.5>
    right x*image_width/image_height
    angle 40
}

#declare Cnt = 0;
#while (Cnt < 25)
    light_source {
        25*(<1, 1, 1>/2 - <rand(RR), rand(RR), rand(RR)>) + <8, 4, 4>
        color 0.6
        fade_distance 3
        fade_power 5
    }
    #declare Cnt = Cnt + 1;
#end

light_source {
    10*<-3, 2, 2>
    color rgb <1.0, 1.0, 1.0>*1.7
    fade_distance 40
    fade_power 10
    shadowless
}
