#include "math.inc"

#declare margin = 0.045; //half of the gap between adjacent tiles.
#declare height = 1;     //height of the tile in the y direction.
#declare rad = 0.04;     //roundness of the edge of the tiles.

// Finish of rhombus
#declare FinRhombus = finish {
    specular 0.3
    roughness 0.2
    reflection 0.3
    phong 0.9
    phong_size 50
}

// Normal of rhombus
#declare NorRhombus = normal {
    bozo 0.8
    scale 0.015
    bump_size 0.4
}

// Texture of thin rhmobus
#declare TexThinRhombus = texture {
    pigment { color rgb <0, 0.27, 0.63> } 
    normal{ NorRhombus }
    finish{ FinRhombus }
}

// Texture of fat rhmobus
#declare TexFatRhombus = texture {
    pigment { color rgb <1, 0.4, 0.8> } 
    normal { NorRhombus }
    finish { FinRhombus }
}

// The main macro for a tile
#macro Rhombus(p1, p2, p3, p4, shape)
    #local ang1 = VAngle(p2-p1, p4-p1)/2;
    #local ang2 = VAngle(p1-p2, p3-p2)/2;
    #local d1 = margin/sin(ang1);
    #local d2 = margin/sin(ang2);
    
    #local w1 = p1-d1*(p1-p3)/vlength(p1-p3);
    #local w3 = p3-d1*(p3-p1)/vlength(p3-p1);
    #local w2 = p2-d2*(p2-p4)/vlength(p2-p4);
    #local w4 = p4-d2*(p4-p2)/vlength(p4-p2);
    
    union {
        prism {
            linear_sweep
            linear_spline
            -height, 0, 5
            w1 w2 w3 w4 w1
        }
        
        sphere   { <w1.x, -rad, w1.y>, rad }
        sphere   { <w2.x, -rad, w2.y>, rad }
        sphere   { <w3.x, -rad, w3.y>, rad }
        sphere   { <w4.x, -rad, w4.y>, rad }
        cylinder { <w1.x, -rad, w1.y>, <w2.x, -rad, w2.y>, rad }
        cylinder { <w2.x, -rad, w2.y>, <w3.x, -rad, w3.y>, rad }
        cylinder { <w3.x, -rad, w3.y>, <w4.x, -rad, w4.y>, rad }
        cylinder { <w4.x, -rad, w4.y>, <w1.x, -rad, w1.y>, rad }
    
        #if (shape=0)
            texture{ TexFatRhombus }
        #else
            texture{ TexThinRhombus }
        #end
    }
#end
