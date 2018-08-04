// Persistence of Vision Ray Tracer Include File
// Vers: 3.7
// Date: 2018/07/27
// Auth: Zhao Liang mathzhaoliang@gmail.com
// Note: settings for size and textures of 4d polytopes
// you should include this file at the beginning of the scene file,
// you may also rewrite these params/macros in the scene file.

#include "colors.inc"

global_settings {
    assumed_gamma 2.2
    max_trace_level 10
}

background { color White }

#declare vertex_size = 0.05;
#declare edge_size = 0.025;
#declare face_transmit = 0.3;

#declare edge_finish = finish {
    metallic
    ambient 0.2
    diffuse 0.7
    brilliance 6
    reflection 0.25
    phong 0.75
    phong_size 80
}

#declare edge_textures = array[4] {
    texture {
        pigment { color Silver }
        finish { edge_finish }
    },
    texture {
        pigment { color Brass }
        finish { edge_finish }
    },
    texture {
        pigment { color Cyan }
        finish { edge_finish }
    },
    texture {
        pigment { color Red }
        finish { edge_finish }
    }
};

#declare face_colors = array[6] { SkyBlue, Violet, Pink, Yellow, Brown, Magenta };

#declare vertex_tex = texture {
    pigment { color Gold }
    finish {
        ambient 0.5
        diffuse 0.5
        reflection 0.1
        roughness 0.03
        specular 0.5
    }
}

#macro edge_tex(i)
    texture { edge_textures[i] }
#end

#macro face_tex(i)
    texture {
        pigment { color face_colors[i] transmit face_transmit }
        finish {
            ambient 0
            diffuse 0.8
            specular 0.5
            reflection 0.2
            roughness 0.001
        }
    }
#end

#macro get_size(q)
    #local len = vlength(q);
    #local len = 2.0 * log(2.0 + len * len);
    len
#end

#macro choose_face(i, face_size)
    #local chosen = false;
    #if (face_size > 0.2 & face_size < 0.8)
        #local chosen = true;
    #end
    chosen
#end
