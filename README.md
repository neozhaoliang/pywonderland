<p align="center"><img src="./alice.png"></p>

# A Tour in the Wonderland of Math with Python

> A collection of python scripts for drawing beautiful figures or animating interesting algorithms in mathematics.

**This repository will be always under construction since there are too many interesting things in math that can be shown by code.** Pull requests, issues, questions, and suggestions are all welcomed!


[![Code Health](https://landscape.io/github/neozhaoliang/pywonderland/master/landscape.svg?style=flat)](https://landscape.io/github/neozhaoliang/pywonderland/master) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![PyPI](https://img.shields.io/pypi/pyversions/Django.svg)]()


## Contents

- [Mandelbrot Set](#mandelbrot-set)
- [Domino Shuffling Algorithm Animation](#domino-shuffling-algorithm-animation)
- [Icosahedral Kaleidoscope](#icosahedral-kaleidoscope)
- [Newton Fractal](#newton-fractal)
- [The E8 Pattern](#the-e8-pattern)
- [The Modular Group](#the-modular-group)
- [Generalized Penrose Tilings](#generalized-penrose-tilings)
- [Wilson's Uniform Spanning Tree Algorithm Animation](#wilsons-uniform-spanning-tree-algorithm-animation)
- [Reaction-Diffusion Simulation](#reaction-diffusion-simulation)
- [The 120-cell](#the-120-cell)

---
### Mandelbrot Set
Mandelbrot 集 [[View Code](./src/misc/mandelbrot.py)]

<br>

<p align="center">
<img src="./img/mandelbrot.png"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Domino Shuffling Algorithm Animation
多米诺洗牌算法 [[View Code](./src/domino/)] [[Arctic Cirlce Phenomena](./img/randomtiling.png)] [[Wiki](https://en.wikipedia.org/wiki/Aztec_diamond)]

<br>

<p align="center">
<img src="./img/dominoshuffling.gif">
</p>

<br>

[[Back to Top](#contents)]

---
### Icosahedral Kaleidoscope

正二十面体万花筒 [[View Code](./src/misc/kaleidoscope.py)] [[View Webm Animation](./img/kaleidoscope.webm)]

<br>

<p align="center">
<img src="./img/kaleidoscope.png"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Newton Fractal
Newton 迭代分形 [[View Code](./src/misc/newton.py)] [[Wiki](https://en.wikipedia.org/wiki/Newton_fractal)]

<br>

<p align="center">
<img src="./img/newton.png"/>
</p>

<br>

[[Back to Top](#contents)]

---
### The E8 Pattern
李代数 E8 的根系 [[View Code](./src/misc/e8.py)] [<a href="https://en.wikipedia.org/wiki/E8_(mathematics)">Wiki</a>]

<br>

<p align="center">
<img src="./img/e8-pattern.png"br/>
</p>

<br>

[[Back to Top](#contents)]

---
### The Modular Group
模群的基本域 [[View Code](./src/misc/modulargroup.py)] [[Wiki](https://en.wikipedia.org/wiki/Modular_group)]

<br>

<p align="center">
<img src="./img/modulargroup.png"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Generalized Penrose Tilings
彭罗斯铺砌 [[View Code](./src/misc/penrose.py)] [[Wiki](https://en.wikipedia.org/wiki/Penrose_tiling)]

<br>

<p align="center">
<img src="./img/penrose.gif"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Wilson's Uniform Spanning Tree Algorithm Animation
Wilson 一致生成树算法 [[View Code](./src/wilson/)] [[Wiki](https://en.wikipedia.org/wiki/Loop-erased_random_walk)] [[Mike Bostock's Javascript Animation](https://bl.ocks.org/mbostock/11357811)]
<br>

<p align="center">
<img src="./img/wilson.gif"/>
</p>

<br>

[[Back to Top](#contents)]

---
### Reaction-Diffusion Simulation
反应扩散方程模拟 [[View Code](./src/grayscott/)] [[Wiki](https://en.wikipedia.org/wiki/Reaction%E2%80%93diffusion_system)] [[View Webm Animation](./img/grayscott.webm)] [[Pmneila's Javascript Animation](http://pmneila.github.io/jsexp/grayscott/)]

<br>

<p align="center">
<img src="./img/grayscott.gif"/>
</p>

<br>

[[Back to Top](#contents)]

---
### The 120-cell
120 胞腔 [[View Code](./src/120cell/)][[Wiki](https://en.wikipedia.org/wiki/120-cell)]

<br>

<p align="center">
<img src="./img/120cell.png"/>
</p>

<br>

[[Back to Top](#contents)]

---
## Dependencies

Python libs:

`numpy`, `matplotlib`, `scipy`, `cairo`, [`palettable`](https://github.com/jiffyclub/palettable), [`tqdm`](https://github.com/tqdm/tqdm), [`numba`](https://github.com/numba/numba), `pyglet`, [`vapory`](https://github.com/Zulko/vapory)

Softwares:

`ImageMagick`, `FFmpeg`, `POV-Ray`
