// Persistence of Vision Ray Tracer Scene Description File
// File: penrose.pov
// Vers: 3.7
// Date: 2018/02/08
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

global_settings {
    assumed_gamma 1.0
    max_trace_level 10
    photons {
        count 200
        autostop 0
    }
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

#declare margin = 0.06; //width of the edge of a tile
#declare height = 0.05; //height of a tile
#declare gap    = 0.03; //gap between adjacent tiles

#declare Normal_Rhombus = normal {
    gradient y
    slope_map {
        [0.0         <0, 1>           ]
        [height*0.5  <height*0.5, 0>  ]
        [height*0.8  <height*0.8, 0.5>]
        [height*0.9  <height*0.9, 0>  ]
        [height*0.95 <height*0.95, 1> ]
        [height      <height, 1>      ]
        [height      <height, -1>     ]
    }
}

#declare Finish_Rhombus = finish {
    ambient 0.1
    diffuse albedo 0.5
    specular albedo 0.3
    roughness 1e-3
    reflection { 0.3 }
}

#declare T_Thin_Rhombus = texture {
    pigment{ SteelBlue }
    normal { Normal_Rhombus }
    finish { Finish_Rhombus }
}
 
#declare T_Fat_Rhombus = texture {
    pigment{ NeonPink }
    normal { Normal_Rhombus }
    finish { Finish_Rhombus }
}

#macro Rhombus(p1, p2, p3, p4, shape)
    #local ang = VAngle(p2-p1, p4-p1)/2;
    #local d = margin/sin(ang);
    #local q1 = p1-d*(p1-p3)/vlength(p1-p3);
    #local q3 = p3-d*(p3-p1)/vlength(p3-p1);
    
    #local ang = VAngle(p1-p2, p3-p2)/2;
    #local d = margin/sin(ang);
    #local q2 = p2-d*(p2-p4)/vlength(p2-p4);
    #local q4 = p4-d*(p4-p2)/vlength(p4-p2);
    
    union {
        prism {
            linear_sweep
            linear_spline
            0, height, 5
            q1 q2 q3 q4 q1
        }
        
        triangle{<p1.x, 0, p1.y>,      <q1.x, height, q1.y>, <p2.x, 0, p2.y>}
        triangle{<q1.x, height, q1.y>, <q2.x, height, q2.y>, <p2.x, 0, p2.y>}
        triangle{<p2.x, 0, p2.y>,      <q2.x, height, q2.y>, <p3.x, 0, p3.y>}
        triangle{<q2.x, height, q2.y>, <q3.x, height, q3.y>, <p3.x, 0, p3.y>}
        triangle{<p3.x, 0, p3.y>,      <q3.x, height, q3.y>, <p4.x, 0, p4.y>}
        triangle{<q3.x, height, q3.y>, <q4.x, height, q4.y>, <p4.x, 0, p4.y>}
        triangle{<p4.x, 0, p4.y>,      <q4.x, height, q4.y>, <p1.x, 0, p1.y>}
        triangle{<q4.x, height, q4.y>, <q1.x, height, q1.y>, <p1.x, 0, p1.y>}
        
        #if (shape=0)
            texture{ T_Fat_Rhombus }
        #else
            texture{ T_Thin_Rhombus }
        #end
        
        scale 0.6
    }
#end

#include "rhombus.pov"

//floor
plane {
    y height*gap/(2*margin)
    pigment{ color rgb 0.1 }
    normal{ bumps 0.5 scale 0.001}
}

//sky
sky_sphere{ pigment{ Blue_Sky }}

//sphere
#declare rad = 2;
sphere {
    <0, 0, 0>, rad
    texture {
        pigment {color rgb 1}
        finish {
            diffuse 0.3
            ambient 0.0
            specular 0.6
            reflection 0.8
        }
    }
    
    photons {
        target
        reflection on
        refraction off
        collect on
    }
    
    translate <0, height+rad, 0>
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
