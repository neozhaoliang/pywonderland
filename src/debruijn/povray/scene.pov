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

#include "tiles.inc"
#include "rhombus.inc"

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
#declare MovStr = "FARATrlRarlFRtAtrtLBTKjRFLtaRRfK";

object {
    RubikCube(MovStr, "T", 0.4)
    scale 0.8
    translate <1, 0, -1>
}

/*=========================================================*/
/* The Lego-style Kites and Darts                          */

#include "kitedart.inc"

union {
    #local K1 = object { Kite translate -phi*z rotate 216*y translate phi*z }
    #local K2 = object { Kite translate -phi*z rotate 144*y translate phi*z }
    #local num=0;
    #while (num<5)
        object { Kite translate -phi*z rotate (72*num+180)*y }
        object { Dart translate  phi*z rotate (72*num+36)*y  }
        object { K1 rotate (72*num)*y }
        object { K2 rotate (72*num)*y }
        object { Dart translate 2*phi*z rotate (72*num)*y }
        #local num=num+1;
    #end
    scale 0.4
    translate <-2, 0, -2>
}
object { Kite scale .4 rotate   90*y  translate <-.5, 0, -3> }
object { Dart scale .4 rotate (-90)*y translate <-.5, 0, -4> }

/*=========================================================*/
/* Floor                                                   */

plane {
    y (-0.001)
    texture {
        pigment { rgb .8 }
        finish {
            specular 0.2
            roughness 0.5
            diffuse 0.8
        }
    }
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
    <0, 1, -1>*50
    color rgb <1, 1, 1>
    fade_distance 40
    fade_power 2
    area_light x*32, y*32, 16, 16 jitter adaptive 2 circular orient
}
