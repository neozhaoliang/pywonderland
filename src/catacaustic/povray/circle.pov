/*
Code adapted from Nicolas Rougier's "ring.pov" file:

    https://www.labri.fr/perso/nrougier/downloads/ring.pov

To render this file, you need to have POV-Ray 3.7 installed.
In terminal, run:

    povray circle.pov +w800 +h600 +fn +am2 +a0.01
 */

#version 3.7;
#include "colors.inc"

global_settings{
    assumed_gamma 1.0
    max_trace_level 25
    photons {
        count 8000000
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

light_source {
    <20, 30, 0>
    rgb <0.75, 1, 1>
    fade_distance 50 fade_power 2
    area_light <10, 0, 0> <0, 0, 10> 20,20  adaptive 0 jitter circular orient
    rotate z*90
    photons {
      reflection on
    }
}

plane {
    y,-2
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
    torus {
        11, 1
        translate  y
    }
    torus {
        11, 1
        translate -y
    }
    cylinder {
        -y, y, 12
        open
    }
    cylinder {
        -y, y, 10
        open
    }
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
}