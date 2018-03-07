#version 3.7;

#include "golds.inc"


global_settings {
    assumed_gamma 1.0
}


#declare rad = 0.08;

#declare T_Edge = texture { T_Gold_5A finish { ambient 0 reflection 0.5 diffuse 0.4 specular 1 } }

#macro Rhombus(p1, p2, p3, p4, shape)
    union {
        cylinder { <p1.x, 0, p1.y>, <p2.x, 0, p2.y>, rad texture{ T_Edge } }
        cylinder { <p2.x, 0, p2.y>, <p3.x, 0, p3.y>, rad texture{ T_Edge } }
        cylinder { <p3.x, 0, p3.y>, <p4.x, 0, p4.y>, rad texture{ T_Edge } }
        cylinder { <p4.x, 0, p4.y>, <p1.x, 0, p1.y>, rad texture{ T_Edge } }
    }
#end

#include "rhombus.inc"

camera {
    location <0, 10, 0>
    look_at <0, 0, 0>
    right x*image_width/image_height
    sky z
}

light_source { 
    <10, 0, -10>
    color rgb <1, 0.8, 0>
}

light_source {
    <0, 1000, 0>
    color rgb <1, 1, 1>
    area_light
    20*x, 20*z, 5, 5
    orient
    jitter
    adaptive 0
}

plane {
    y (-5)
    pigment {color rgb 0.2}
}
