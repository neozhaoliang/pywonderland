#coding = utf-8

from automata import *
from collections import deque
import numpy as np
from numpy import pi, sin, cos, sqrt
import cairo


alpha, beta, gamma = pi/4, pi/3, pi/3
coshb = (cos(beta)+cos(alpha)*cos(gamma))/(sin(alpha)*sin(gamma))
coshc = (cos(gamma)+cos(alpha)*cos(beta))/(sin(alpha)*sin(beta))
rB = sqrt((coshb-1)/(coshb+1))
rC = sqrt((coshc-1)/(coshc+1))

sina = sin(alpha)
cosa = cos(alpha)
v = cosa + sina*1j
A = 0j
B = rB
C = rC*v
fundamental_domain = [A, B, C]
eps = 1e-8  


def mobius(z, theta=0, a=0):
    return np.exp(theta*1j) * (z-a) / (1-z*a.conjugate())
    
def compute_circle(x0, y0, x1, y1):
    """
    compute the geodesic circle that passes through (x0,y0) and (x1,y1) 
    """
    
    # return None if they are close enough or on the same diameter
    t = 2*(x0*y1 - x1*y0)
    if abs(t) < eps:
        return None

    r0 = 1 + x0**2 + y0**2
    r1 = 1 + x1**2 + y1**2
    cen_x = (y1*r0-y0*r1) / t
    cen_y = (x0*r1-x1*r0) / t
    r = np.sqrt(cen_x**2+cen_y**2-1)
    return cen_x, cen_y, r

cen_x, cen_y, r = compute_circle(rB, 0, C.real, C.imag)
cen = cen_x + cen_y*1j

def ref_by_AB(z):
    return z.conjugate()
    
def ref_by_AC(z):
    return 2*(z.real*cosa+z.imag*sina)*v - z

def ref_by_BC(z):
    return cen + r**2 / (z-cen).conjugate()
    
transformations = [ref_by_AB, ref_by_AC, ref_by_BC]

def transform(symbol, shape):
    return [transformations[symbol](z) for z in shape]

def traverse(dfa, depth, fundamental_shape):
    """
    traverse the given dfa. One can use either bread-first or depth-first search. 
    """
    queue = deque()
    queue.append(["", dfa.initial, 0, fundamental_shape] )
        
    while queue:
        word, state, i, shape = queue.popleft()
        yield word, state, i, shape
            
        if i < depth:
            for symbol, target in state.all_transitions():
                queue.append( [word+str(symbol), target, i+1, transform(symbol, shape)] )
          
def arc_to(cr, x1, y1):
    x0, y0 = cr.get_current_point()
    
    try:
        c_x, c_y, R = compute_circle(x0, y0, x1, y1)

        A0 = np.arctan2(y0-c_y, x0-c_x)
        A1 = np.arctan2(y1-c_y, x1-c_x)
        
        if abs(A0-A1) <= pi:
            if A0 < A1:
                cr.arc(c_x, c_y, R, A0, A1)
            else:
                cr.arc_negative(c_x, c_y, R, A0, A1)
        else:
            if A0 < A1:
                cr.arc_negative(c_x, c_y, R, A0, A1)
            else:
                cr.arc(c_x, c_y, R, A0, A1)
    except:
        cr.line_to(x1, y1)

coxeter_dfa = Parse("coxeter_433.txt").asDFA().draw("coxeter_433-dfa.png")

surface = cairo.SVGSurface("poincare_433.svg", 600, 600)
cr = cairo.Context(surface)
cr.scale(300,-300)
cr.translate(1,-1)
cr.scale(0.9, 0.9)
cr.set_source_rgb(1,1,1)
cr.paint()

cr.set_line_join(2)
cr.set_line_cap(2)

depth = 18

for w, state, i, tri in traverse(coxeter_dfa, depth, fundamental_domain):
    
    tri = [ mobius(z) for z in tri ]
    z1, z2, z3= tri
    
    cr.move_to(z1.real, z1.imag)
    arc_to(cr,z2.real,z2.imag)
    arc_to(cr,z3.real,z3.imag)
    arc_to(cr,z1.real,z1.imag)
    cr.close_path()

    if w:
         if len(w) % 2 == 0:
              cr.set_source_rgb(1, 0.75, 0.5)
         else:
              cr.set_source_rgb(0, 0.5, 1)

    else:
         cr.set_source_rgb(0.5, 0.5, 0.5)
         
    cr.fill_preserve()
    cr.set_source_rgb(0, 0, 0)
    cr.set_line_width(0.005)
    cr.stroke()
    
cr.arc(0, 0, 1, 0, 2*pi)
cr.set_source_rgb(0,0,0)
cr.set_line_width(0.005)
cr.stroke()

surface.finish()
