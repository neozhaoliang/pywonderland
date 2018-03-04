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

- [Reaction-Diffusion Simulation](#reaction-diffusion-simulation)
- [The E8 Pattern](#the-e8-pattern)
- [Icosahedral Kaleidoscope](#icosahedral-kaleidoscope)
- [Domino Shuffling Algorithm Animation](#domino-shuffling-algorithm-animation)
- [Wilson's Uniform Spanning Tree Algorithm Animation](#wilsons-uniform-spanning-tree-algorithm-animation)
- [Coupling From The Past and Lozenge Tilings](#coupling-from-the-past-and-lozenge-tilings)

---
### Icosahedral Kaleidoscope
[[View Code](./src/misc/kaleidoscope.py)]

<br>

<p align="center">
<img src="http://www.pywonderland.com/img/kaleidoscope.png"br/>
</p>

<br>

[[Back to Top](#contents)]

---
### Reaction-Diffusion Simulation
[[View Code](./src/grayscott/)] [[Pmneila's Javascript Animation](http://pmneila.github.io/jsexp/grayscott/)]

<br>

<p align="center">
<img src="http://www.pywonderland.com/img/grayscott/unstable.png"/>
</p>

<br>

[[Back to Top](#contents)]

---
### The E8 Pattern
[[View Code](./src/misc/e8.py)] [<a href="https://en.wikipedia.org/wiki/E8_(mathematics)">Wiki</a>]

<br>

<p align="center">
<img src="http://www.pywonderland.com/img/E8.png"br/>
</p>

<br>

[[Back to Top](#contents)]

---
### Domino Shuffling Algorithm Animation
[[View Code](./src/domino/)]
<br>

<p align="center">
<img src="http://www.pywonderland.com/img/aztec/domino_shuffling.gif">
</p>

<br>

[[Back to Top](#contents)]

---
### Wilson's Uniform Spanning Tree Algorithm Animation
[[View Code](./src/wilson/)] [[Mike Bostock's Javascript Animation](https://bl.ocks.org/mbostock/11357811)]
<br>

<p align="center">
<img src="http://www.pywonderland.com/img/wilson/wilson-bfs.gif"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Coupling from the past and lozenge tilings
[[View Code](./src/cftp/)]
<br>

<p align="center">
<img src="http://www.pywonderland.com/img/cftp/lozenge_tiling.png"/>
</p>

<br>

[[Back to Top](#contents)]


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