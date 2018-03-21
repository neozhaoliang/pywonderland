// Persistence of Vision Ray Tracer Scene Description File
// File: penrose.pov
// Vers: 3.7
// Date: 2018/02/08
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

global_settings {
    assumed_gamma 1.0
    radiosity {
        pretrace_start 0.08
        pretrace_end   0.01
        count 100
        error_bound 0.2
    }
}

#include "textures.inc"
#include "colors.inc"
#include "math.inc"

#declare tile_margin = 0.02;
#declare tile_height = 0.05;

#declare Finish_Rhombus = finish {
    diffuse 0.5
    specular 0.3
    roughness 0.1
    reflection 0.3
}

#declare ThinRhombusTex = texture {
    pigment{ SteelBlue }
    finish { Finish_Rhombus }
}
 
#declare FatRhombusTex = texture {
    pigment{ NeonPink }
    finish { Finish_Rhombus }
}

#macro Rhombus(p1, p2, p3, p4, shape)
    #local ang1 = VAngle(p2-p1, p4-p1)/2;
    #local ang2 = VAngle(p1-p2, p3-p2)/2;
    #local d1 = tile_margin/sin(ang1);
    #local d2 = tile_margin/sin(ang2);

    #local w1 = p1-d1*(p1-p3)/vlength(p1-p3);
    #local w3 = p3-d1*(p3-p1)/vlength(p3-p1);
    #local w2 = p2-d2*(p2-p4)/vlength(p2-p4);
    #local w4 = p4-d2*(p4-p2)/vlength(p4-p2);

    prism {
        linear_sweep
        linear_spline
        -tile_height, 0, 5
        w1 w2 w3 w4 w1
    
        #if (shape=0)
            texture{ FatRhombusTex }
        #else
            texture{ ThinRhombusTex }
        #end
    }
#end

#include "rhombus.inc"

//floor
plane {
    y (-0.01)
    pigment{ color rgb 0.1 }
    normal{ bumps 0.5 scale 0.001 }
}

//sky
sky_sphere{ pigment{ Blue_Sky } }

//sphere
#declare rad = 2;
sphere {
    <0, 0, 0>, rad
    texture {
        pigment { color rgb 1 }
        finish {
            diffuse 0.3
            specular 0.6
            reflection 0.8
        }
    } 
    translate <0, tile_height+rad, 0>
}

camera {
    location <-4, 6, -8>
    look_at <0, 0, 0>
    right x*image_width/image_height
}

light_source {
    <1, 1, -1>*3000
    color rgb <1, 1, 1>
}
