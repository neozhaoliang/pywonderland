/*
Code adapted from Nicolas Rougier's "ring.pov" file.

To render this file, you need to have POV-Ray 3.7 installed.
In terminal, run:

    povray cardioid.pov +w800 +h600 +fn +am2 +a0.01

The scene contains:

1. A plane y = -2 with a checkerboard pattern.
2. A parametric surface defined by the functions:
    x(u, v) = (2*cos(u) + cos(2*u)) / 3
    y(u, v) = v
    z(u, v) = (2*sin(u) + sin(2*u)) / 3
    This is a cylinder with a cardioid cross-section. from y=-1 to y=1.
3. Two sphere_sweep objects that are placed on the top and bottom rims of the cylinder.
   Note that the spheres do not have the same radius, hence the bottom rim does not
   lie on the same horizontal plane. This may cause some artifacts in the rendering.
 */
#version 3.7;
#include "colors.inc"
#include "math.inc"

global_settings{
    assumed_gamma 1.0
    max_trace_level 25
    photons {
        spacing .01
        autostop 0
        gather 0, 200
        jitter 0.4
    }
    radiosity {
        pretrace_start 0.08
        pretrace_end   0.01
        count 600
        error_bound .25
        nearest_count 8
        recursion_limit 1
        gray_threshold 0
        minimum_reuse 0.015
        brightness 1.0
        adc_bailout 0.01/2
  }
}

#include "screen.inc"
#declare EyePos = <0,60,10>;
#declare EyeLook = <0,0,0>;
#declare EyeAngle = 40;
Set_Camera(EyePos, EyeLook, EyeAngle)

#macro Cx(T)
    (2*cos(T) + cos(2*T)) / 3
#end

#macro Cz(T)
    (2*sin(T) + sin(2*T)) / 3
#end

#macro param_surf(sc)
    parametric {
        function { (2*cos(u) + cos(2*u)) / 3 }
        function { v }
        function { (2*sin(u) + sin(2*u)) / 3 }
        <0, -1>, <2*pi, 1>
        scale <sc, 1.0, sc>
    }
#end

#macro get_radius(T)
    #local rad = vlength(<Cx(T), 0, Cz(T)>);
    rad
#end

#macro tube(sc, ht)
    #local num_segments = 120;
    sphere_sweep {
        cubic_spline
        num_segments + 3
        <sc * Cx(0), ht, sc * Cz(0)>, get_radius(0)
        #local j = 0;
        #while (j < num_segments + 1)
            #local T = 2*pi*j/num_segments;
            #local P = <sc * Cx(T), ht, sc * Cz(T)>;
            #local Q = <Cx(T), 0, Cz(T)>;
            #local rad = vlength(Q);
            #local j = j + 1;
            P, rad
        #end
        <sc * Cx(0), ht, sc * Cz(0)>, get_radius(0)
    }
#end


light_source {
    <10, 16, 0> // will be rotated to <-16, 10, 0>
    rgb <0.75, 1, 1>
    fade_distance 50 fade_power 2
    area_light <10, 0, 0> <0, 0, 10> 20,20  adaptive 0 jitter circular orient
    rotate z*90
    photons {
      reflection on
    }
}

plane {
    y, -2
    pigment {
        checker
        color rgb 1, color rgb 0.8
    }
    finish {
        reflection 0.2
        diffuse 0.3
        specular 0.4
    }
    photons {
        target
        collect on
        reflection off
        refraction off
    }
}

union {
    #local sc = 14;
    object { param_surf(sc) }
    object { param_surf(sc + 2) }
    object { tube(sc + 1, -1) }
    object { tube(sc + 1, 1) }
    pigment {
        rgb .1
    }
    finish {
        reflection .9
        specular 3
        roughness 0.0025
        ambient 0
        diffuse 1
    }
    photons {
        target
        reflection on
        collect on
    }
    translate -3 * x
}