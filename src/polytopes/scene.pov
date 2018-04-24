// Persistence of Vision Ray Tracer Scene Description File
// Vers: 3.7
// Date: 2018/04/22
// Auth: Zhao Liang mathzhaoliang@gmail.com

#version 3.7;

global_settings {
    assumed_gamma 1.0
}

background { rgb <0.2, 0.4, 0.9> }

#include "metals.inc"

// adjust the vertex and edge radius here
#declare vRad = 0.07;
#declare eRad = 0.03;
#declare numSegments = 30;

// adjust the camera position for rendering different polytopes
camera {
    location <0, 2.5, -1.5>*12  //*35 for 120-cell
    look_at <0, 0, 0>
    right x*image_width/image_height
}

#declare Metal = texture {
    pigment { P_Chrome2 }
    finish {
        ambient 0
        diffuse 0.3
        specular 1.4
        roughness 0.020962
        metallic
        reflection {
            0.35, 0.7
            metallic
        }
        conserve_energy
        brilliance 2
    }
    normal {
        granite -0.02
        poly_wave 4
    }
}

#macro Proj(p)
    #local q = p / sqrt(p.x*p.x + p.y*p.y + p.z*p.z + p.t*p.t);
    <q.x, q.y, q.z> / (1.0 + q.t)
#end

#macro Vertex(p)
    sphere {
        Proj(p), vRad*vlength(Proj(p))
        pigment {
            color rgb <0.8, 0.8, 0.2>
        }
        finish {
            diffuse 0.7 specular 0.3 roughness 0.003
        }
    }
#end

#macro Arc(p1, p2)
    sphere_sweep {
        cubic_spline
        numSegments + 3,
        Proj(p1), eRad*vlength(Proj(p1))
        #local i=0;
        #while (i < numSegments)
            #local q = Proj(p1 + i*(p2-p1)/numSegments);
            q, eRad*vlength(q)
            #local i=i+1;
        #end
        Proj(p2), eRad*vlength(Proj(p2))
        Proj(p2), eRad*vlength(Proj(p2))
        texture { Metal }
    }
#end

union {
    #include "polytope-data.inc"
    scale 8
}

light_source
{ <50, 50, -50>, 1
  area_light x*3, y*3, 12, 12 circular orient adaptive 0
}

light_source
{ <40, 50, 40>, 1
  area_light x*3, y*3, 12, 12 circular orient adaptive 0
}


light_source
{ <0, 60, 0>, 1
  area_light x*3, y*3, 12, 12 circular orient adaptive 0
}

light_source
{ <0, -20, 0>, 1
  area_light x*3, y*3, 12, 12 circular orient adaptive 0
}
