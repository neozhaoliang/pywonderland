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

/*=== tiles ===*/

#include "penrose.inc"
#include "rhombus.inc"

/*=== floor ===*/

plane {
    y (-rad*0.4)
    texture {
        pigment { rgb 1 }
        finish { diffuse 0.7 specular 0.6 roughness 0.15} 
        normal { granite 0.15 scale 0.25 bump_size 0.15 }
    }
}

/*=== the rubik's cube ===*/

#include "rubik.inc"

#declare tTmp = array[3][3][3]          // Temporary translation array
#declare MvStr = "FARATrlRarlFRtAtrtLB" // Move string to scramble the cube
#declare SStrX = "TBTBTFlbtlbtbFbffbFBfbFBABaRbrBRbrBbbABaBLbllBLBFbfbrbRbfBFBBabA"
#declare SStrY = "bRBrRbfBFrAAttRRTFFLLFFLLFFLLtRRttAAlTLtlTLtblTLtlTLtblTLtlTLtbb"
#declare SStr  = concat(SStrX, SStrY)   // Move string to solve the cube
#declare MStr  = concat(MvStr, SStr)    // Complete move string

Manip(Tran, iTran, SStr)                            // Twist the cube
Rot("T", tTmp, Tran, iTran, 0.4)                    // Twist a slice just a little
object {
    Rubik(Cubes, tTmp)
    scale 0.8
    translate <1, 1.2, -1>
}

/*=== the icosahedron ===*/

#include "icosa.inc"

#declare REdge = 0.03;
#declare RVert = 0.06;
#declare icosa = object {
    Platonic_icosahedron_faces(yes)
    finish { FinFace }
    normal { NorFace }
}


#declare TexIcosaEdge = texture {
    pigment { color rgb <0.05, 0.05, 0.05> }
    finish { FinFace }
}

#declare TexIcosaVert = TexIcosaEdge
    
#declare edges = object {
    Platonic_icosahedron_edges(REdge, RVert, TexIcosaEdge, TexIcosaVert, yes)
}
 
union {
    object { 
        icosa 
        texture { 
            finish { FinFace } 
            normal { NorFace }
        } 
        translate <0, RVert, 0>
    }
    object { 
        edges 
        texture {
            finish {
                specular 0.05
                diffuse 0.7
                reflection 0.1
            }
        }
    }
    rotate <0, 30, 0>
    translate <-2, 0, 1>
}

/*=== camera and lights ===*/

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
    <0, 1, 0>*100
    color rgb <1, 1, 1>
    fade_distance 35
    fade_power 2
    area_light x*4, z*4, 16, 16 jitter adaptive 2 circular orient
}
