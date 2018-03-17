# A Tour in the Wonderland of Math with Python

<p align="center"><img src="./alice.png"></p>


> A collection of python scripts for drawing beautiful figures or animating interesting algorithms in mathematics.

[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT) [![PyPI](https://img.shields.io/pypi/pyversions/Django.svg)]()


## About this repo

Please visit [the website for this repository](http://www.pywonderland.com) to see how to use these scripts and get more information of the math behind them.

I'm building the docs so that there will be more usage & math explanations for each program.

The history commits are deleted (sorry for this) but will not be deleted any more.

**This repository will be always under construction since there are too many interesting things in math that can be shown by code.** Pull requests, issues, questions, and suggestions are all welcomed!

## Contents

- [Mandelbrot Set](#mandelbrot-set)
- [Julia Set](#julia-set)
- [Newton Fractal](#newton-fractal)
- [Icosahedral Kaleidoscope](#icosahedral-kaleidoscope)
- [Reaction-Diffusion Simulation](#reaction-diffusion-simulation)
- [The E8 Pattern](#the-e8-pattern)
- [The Modular Group](#the-modular-group)
- [Generalized Penrose Tilings](#generalized-penrose-tilings)
- [Domino Shuffling Algorithm Animation](#domino-shuffling-algorithm-animation)
- [Wilson's Uniform Spanning Tree Algorithm Animation](#wilsons-uniform-spanning-tree-algorithm-animation)
- [Coupling From The Past And Lozenge Tilings](#coupling-from-the-past-and-lozenge-tilings)

---
### Mandelbrot Set
[[Code](./src/misc/mandelbrot.py)] [[Doc](http://www.pywonderland.com/fractals-numpy/)]

<br>

<p align="center">
<img src="http://www.pywonderland.com/img/fractals/mandelbrot.png" width="600"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Julia Set
[[Code](./src/misc/julia.py)] [[Doc](http://www.pywonderland.com/fractals-numpy/)]

<br>

<p align="center">
<img src="http://www.pywonderland.com/img/fractals/julia.png" width="600"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Newton Fractal
[[Code](./src/misc/newton.py)] [[Doc](http://www.pywonderland.com/fractals-numpy/)]

<br>

<p align="center">
<img src="http://www.pywonderland.com/img/fractals/newton.png" width="500"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Icosahedral Kaleidoscope
[[Code](./src/misc/kaleidoscope.py)] [[Doc](http://www.pywonderland.com/kaleidoscope/)]

<br>

<p align="center">
<img src="http://www.pywonderland.com/img/icosa/kaleidoscope.png"br/>
</p>

<br>

[[Back to Top](#contents)]

---
### Reaction-Diffusion Simulation
[[Code](./src/grayscott/)] [[Doc](http://www.pywonderland.com/grayscott/)] [[Pmneila's Javascript Animation](http://pmneila.github.io/jsexp/grayscott/)]

<br>

<p align="center">
<img src="http://www.pywonderland.com/img/grayscott/unstable.png"/>
</p>

<br>

[[Back to Top](#contents)]

---
### The E8 Pattern
[[Code](./src/misc/e8.py)] [[Doc](http://www.pywonderland.com/e8/)] [<a href="https://en.wikipedia.org/wiki/E8_(mathematics)">Wiki</a>]

<br>

<p align="center">
<img src="http://www.pywonderland.com/img/E8.png"br/>
</p>

<br>

[[Back to Top](#contents)]

---
### The Modular Group
[[Code](./src/misc/modulargroup.py)] [[Doc](http://www.pywonderland.com/modular/)] [[Wiki](https://en.wikipedia.org/wiki/Modular_group)]

<br>

<p align="center">
<img src="http://www.pywonderland.com/img/modular/modulargroup.png"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Generalized Penrose Tilings
[[Code](./src/penrose/)] [[Doc](http://www.pywonderland.com/penrose/)]

<br>

<p align="center">
<img src="http://pywonderland.com/img/penrose/penrose_star.png" width="350"/><img src="http://pywonderland.com/img/penrose/penrose_net.png" width="350"/>
<img src="http://pywonderland.com/img/penrose/penrose_kitedart.png" width="350"/><img src="http://pywonderland.com/img/penrose/penrose_scene.png" width="350"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Domino Shuffling Algorithm Animation
[[Code](./src/domino/)][[Doc](http://www.pywonderland.com/aztec/)]
<br>

<p align="center">
<img src="http://www.pywonderland.com/img/aztec/domino_shuffling.gif">
</p>

<br>

[[Back to Top](#contents)]

---
### Wilson's Uniform Spanning Tree Algorithm Animation
[[Code](./src/wilson/)] [[Doc](http://www.pywonderland.com/wilson/)] [[Mike Bostock's Javascript Animation](https://bl.ocks.org/mbostock/11357811)]
<br>

<p align="center">
<img src="http://www.pywonderland.com/img/wilson/wilson-bfs.gif"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Coupling From The Past And Lozenge Tilings
[[Code](./src/cftp/)] [[Doc](http://www.pywonderland.com/cftp/)]
<br>

<p align="center">
<img src="http://www.pywonderland.com/img/cftp/lozenge_tiling.png"/>
</p>

<br>

[[Back to Top](#contents)]

---
## Programs to come:

- Fractals with orbit trap
- 2D hyperbolic tilings (Escher's circle limit)
- 3D hyperbolic honeycombs
- 4D regular polytopes
- Hopcroft's minimization algorithm

## Dependencies

Python libs:

+ `numpy`
+ `matplotlib`
+ `cairo`
+ [`palettable`](https://github.com/jiffyclub/palettable)
+ [`numba`](https://github.com/numba/numba)
+ `pyglet`

Softwares:

+ `ImageMagick`
+ `FFmpeg`
+ `POV-Ray`
