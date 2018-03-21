// Persistence of Vision Ray Tracer Scene Include File
// File: kitedart.inc
// Vers: 3.7
// Date: 2018/03/15
// Auth: Zhao Liang mathzhaoliang@gmail.com

#include "math.inc"
#include "colors.inc"

/*==========================================================*/
/* Params for a tile                                        */

#declare phi = (1 + sqrt(5)) / 2;
#declare tile_gap = 0.005;
#declare tile_height = 0.2;

/*==========================================================*/
/* Texture of the tile                                      */

#declare TileFinish = finish {
    specular 2
    roughness 0.025
    phong 0.6 phong_size 100
    diffuse 0.7
    reflection 0.1
}

#declare TileNormal = normal { bozo 0.005 scale 0.001 }

#declare KiteTexture = texture {
    pigment { BrightGold }
    finish { TileFinish }
    normal { TileNormal }
}

#declare DartTexture = texture {
    pigment { SlateBlue }
    finish { TileFinish }
    normal { TileNormal }
}

#declare TileEdgeTexture = texture {
    pigment { color rgb 0.05 }
    finish { TileFinish }
}

/*==========================================================*/
/* Vertices for the tiles                                   */

#declare vKite = array[4] {
    <0, 0, 0>, <cos(pi/10), 0, sin(pi/10)>, <0, 0, phi>, <-cos(pi/10), 0, sin(pi/10)>
}

#declare vDart = array[4] {
    <0, 0, 0>, <cos(pi/10), 0, -sin(pi/10)>, <0, 0, 1>, <-cos(pi/10), 0, -sin(pi/10)>
}

// a smaller tile with some gap between the original tile
#macro smallKite(gap)
    array[4] {
        <0, 0,   gap/sin(2*pi/5)>,   vKite[1]+gap/sin(pi/5)*<-cos(pi/10), 0, sin(pi/10)>,
        <0, 0, phi-gap/sin(pi/5)>,   vKite[3]+gap/sin(pi/5)*< cos(pi/10), 0, sin(pi/10)>
    }
#end

#macro smallDart(gap)
    array[4] {
        <0, 0, gap/sin(2*pi/5)>, vDart[1]+gap/sin(pi/10)*<-cos(pi/5), 0, sin(pi/5)>,
        <0, 0, 1-gap/sin(pi/5)>, vDart[3]+gap/sin(pi/10)*< cos(pi/5), 0, sin(pi/5)>
    }
#end

/*==========================================================*/
/* Kite and Dart                                            */

// Undecorated kite
#declare iKite = prism {
    #local verts = smallKite(tile_gap);
    linear_sweep
    linear_spline
    0, tile_height, 5
    <verts[0].x, verts[0].z>
    <verts[1].x, verts[1].z>
    <verts[2].x, verts[2].z>
    <verts[3].x, verts[3].z>
    <verts[0].x, verts[0].z>

    texture { TileEdgeTexture }
}

// Undecorated dart
#declare iDart = prism {
    #local verts = smallDart(tile_gap);
    linear_sweep
    linear_spline
    0, tile_height, 5
    <verts[0].x, verts[0].z>
    <verts[1].x, verts[1].z>
    <verts[2].x, verts[2].z>
    <verts[3].x, verts[3].z>
    <verts[0].x, verts[0].z>

    texture { TileEdgeTexture }
}

// The kite
#declare Kite = union {
    #local verts = smallKite(tile_gap+0.03);
    object { iKite }
    prism {
        linear_sweep
        linear_spline
        0.001, tile_height+0.001, 5
        <verts[0].x, verts[0].z>
        <verts[1].x, verts[1].z>
        <verts[2].x, verts[2].z>
        <verts[3].x, verts[3].z>
        <verts[0].x, verts[0].z>
        
        texture { KiteTexture }
    }
}

// The dart
#declare Dart = union {
    #local verts = smallDart(tile_gap+0.03);
    object { iDart }
    prism {
        linear_sweep
        linear_spline
        0.001, tile_height+0.001, 5
        <verts[0].x, verts[0].z>
        <verts[1].x, verts[1].z>
        <verts[2].x, verts[2].z>
        <verts[3].x, verts[3].z>
        <verts[0].x, verts[0].z>
        
        texture { DartTexture }
    }
}
