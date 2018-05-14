// Persistence of Vision Ray Tracer Scene Include File
// File: penrose.inc
// Vers: 3.7
// Date: 2018/02/08
// Auth: Zhao Liang mathzhaoliang@gmail.com

#include "math.inc"
#include "colors.inc"
#include "stones.inc"

// ===================================================================
// You should define these before using the Rhombus macro

#declare tile_gap = 0.02;     //half the gap between adjacent tiles.
#declare tile_height = 1;     //height of the tile.

//====================================================================
// Textures of the rhombus

#declare RhombusNormal = normal {
    average
    normal_map {
        [ .5 wrinkles .3 scale 20 ]
        [ .5 bumps .01 scale .3 ]
        [ .5 agate .13 turbulence .18 scale 6 ]
    }
    scale <3,1,1>
}

#declare RhombusFinish = finish {
    ambient 0
    diffuse .9
    reflection 0.1
    specular .1
    roughness .6
}

#declare RhombusTex1 = texture {
    pigment { rgb <0.9, 0.87, 0.8> }
    finish { RhombusFinish }
    normal {  RhombusNormal }
}

#declare RhombusTex2 = texture {
    pigment { rgb <0.1, 0.23, 0.3> }
    finish { RhombusFinish }
    normal {  RhombusNormal }
}

// Texture of thin rhmobus
#declare ThinRhombusTex = texture {
    average
    texture_map {
        [0.6 RhombusTex1]
        [0.4 T_Stone1 scale 0.5]
    }
}

// Texture of thin rhmobus
#declare FatRhombusTex = texture {
    average
    texture_map {
        [0.6 RhombusTex2]
        [0.4 T_Stone19 scale 0.2]
    }
}

// ========================================================
// The main macro for a tile
#macro Rhombus(p1, p2, p3, p4, shape)
    #local ang1 = VAngle(p2-p1, p4-p1)/2;
    #local ang2 = VAngle(p1-p2, p3-p2)/2;
    #local d1 = tile_gap/sin(ang1);
    #local d2 = tile_gap/sin(ang2);

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
