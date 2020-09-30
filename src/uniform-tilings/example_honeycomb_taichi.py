import numpy as np
import taichi as ti
import coxeter as cx


ti.init(debug=False, arch=ti.gpu)

@ti.func
def hdot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2] - v1[3] * v2[3]
