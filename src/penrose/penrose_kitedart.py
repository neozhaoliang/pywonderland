# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Penrose Tiling by Kites and Darts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import cairocffi as cairo
import numpy as np


num_divides = 6
radius = 10
phi = (np.sqrt(5) - 1) / 2


def htmlcolor_to_rgb(s):
    if len(s) != 6:
        raise ValueError("Bad html color format. Expected: 'RRGGBB' ")
    return [int(n, 16) / 255.0 for n in (s[0:2], s[2:4], s[4:])]


def subdivide_kite_dart(triangles): 
    result = [] 
    for color, A, B, C in triangles: 
        if color == 0: 
            # subdivide red (sharp isosceles) (half kite) triangle 
            Q = A + (B - A) * phi
            R = B + (C - B) * phi
            result += [(1, R, Q, B), (0, Q, A, R), (0, C, A, R)] 
        else: 
            # subdivide blue (fat isosceles) (half dart) triangle 
            P = C + (A - C) * phi
            result += [(1, B, P, A), (0, P, C, B)] 
        
    return result 

triangles = []
for i in range(10):
    B = radius * np.exp((2*i - 1) * np.pi * 1j / 10)
    C = radius * np.exp((2*i + 1) * np.pi * 1j / 10)
    if i % 2 == 0:
        B, C = C, B
    triangles.append((0, B, 0j, C))  # note the order of the vertices here!
    
# perform subdivisions
for i in range(num_divides):
    triangles = subdivide_kite_dart(triangles)

size = (800, 600)
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size[0], size[1])
ctx = cairo.Context(surface)
ctx.translate(size[0] / 2.0, size[1] / 2.0)
extent = max(size) / (radius * 1.2)
ctx.scale(extent, extent)

# draw red triangles
for color, A, B, C in triangles:
    if color == 0:
        ctx.move_to(A.real, A.imag)
        ctx.line_to(B.real, B.imag)
        ctx.line_to(C.real, C.imag)
        ctx.close_path()

ctx.set_source_rgb(*htmlcolor_to_rgb("E41A1C"))
ctx.fill()

# draw blue triangles
for color, A, B, C in triangles:
    if color == 1:
        ctx.move_to(A.real, A.imag)
        ctx.line_to(B.real, B.imag)
        ctx.line_to(C.real, C.imag)
        ctx.close_path()

ctx.set_source_rgb(*htmlcolor_to_rgb("FF7F00"))
ctx.fill()

color, A, B, C = triangles[0]
ctx.set_line_width(abs(B - A)/10.0)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)
ctx.set_source_rgb(*htmlcolor_to_rgb("377EB8"))

for color, A, B, C in triangles:
    ctx.move_to(B.real, B.imag)
    ctx.line_to(A.real, A.imag)
    ctx.line_to(C.real, C.imag)
    ctx.stroke()
    
surface.write_to_png("penrose_kitedart.png")
