#version 3.7;

global_settings {
  assumed_gamma 2.2
  max_trace_level 10
}

#declare TubeThickness = 0.05;

#macro Torus(center, rad, mat, col)
  torus {
    rad, TubeThickness
    texture {
      pigment { color col }
      finish { ambient 0.4 diffuse 0.5 specular 0.6 roughness 0.1 reflection 0 }
    }
    matrix<
    mat[0].x, mat[0].y, mat[0].z,
    mat[1].x, mat[1].y, mat[1].z,
    mat[2].x, mat[2].y, mat[2].z,
    0,        0,        0
    >
    translate center
  }
#end

union {
  #include "torus-data.inc"
}

camera {
  location <0, 0, 1> * 9
  look_at <0, 0, 0>
  right x*image_width/image_height
  up y
  sky y
}

light_source {
  <0, 1, 1> * 100
  color rgb 1
  area_light
  x*32, z*32, 5, 5
  adaptive 1
  jitter
}
