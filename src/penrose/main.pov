// Persistence of Vision Ray Tracer Scene Description File
// File: penrose.pov
// Vers: 3.7
// Date: 2018/02/08
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

global_settings {
    assumed_gamma 1.0
    max_trace_level 10
    ambient_light 0
    radiosity {
        count 100
        error_bound 0.1
        recursion_limit 5
    }
}

/*=========================================================*/
/* Tiling                                                  */

#include "penrose.inc"
#include "rhombus.inc"

/*=========================================================*/
/* Floor                                                   */

// tile_rad is defined in penrose.inc
plane {
    y (-tile_rad*0.4)
    texture {
        pigment { rgb 1 }
        finish { diffuse 0.7 specular 0.6 roughness 0.15} 
        normal { granite 0.15 scale 0.25 bump_size 0.15 }
    }
}

/*=========================================================*/
/* Icosahedron                                             */

#include "icosa.inc"

object {
    Icosahedron
    scale 0.6 rotate -30*y translate <-2, 0, 1>
}

/*=========================================================*/
/* Rubik's cube                                            */

#include "rubik.inc"

// moves that scrambel the cube
#declare MovStr = "FARATrlRarlFRtAtrtLB";

object {
    RubikCube(MovStr, "T", 0.4)
    scale 0.8
    translate <1, 0, -1>
}

/*=========================================================*/
/* Camera and Lights                                       */

camera {
    location <-2, 7, -12>
    look_at <0, 0, 0>
    angle 35
    right x*image_width/image_height
}

light_source {
    <0, 6, -10>
    color rgb <1, 1, 1>
    cylinder
    radius 2
    falloff 4
    point_at <-0.5, 0, 1.2>
}

light_source {
    <0, 1, -1>*100
    color rgb <1, 1, 1>
    fade_distance 60
    fade_power 2
    area_light x*32, y*32, 16, 16 jitter adaptive 2 circular orient
}
