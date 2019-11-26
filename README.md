<p align="center">
<img src="120-cell.png" width="400">
</p>

# A Tour in the Wonderland of Math with Python

<br>

> #### A collection of python scripts for drawing beautiful figures and animating interesting algorithms in mathematics.

<br>

[![Build Status](https://travis-ci.org/neozhaoliang/pywonderland.svg?branch=master)](https://travis-ci.org/neozhaoliang/pywonderland) ![](https://img.shields.io/badge/license-MIT-blue.svg) ![](https://img.shields.io/badge/python-3.5%20%7C%203.6-orange.svg)

<br>


## About this repo

Math is beautiful, but to truly enjoy it one has to walk a long and painful way learning lots of boring stuff before he could see the full landscape. I hope this repo could help those people without a strong math background get some intuitive understanding of the beauty and elegance of math. The topics are chosen largely due to my personal taste:

1. They must produce appealing results.
2. There must be some non-trivial math behind them.
3. The code should be as simple as possible.

I'll use only popular python libs and build all math stuff by hand (tools like `sage`, `sympy`, `mathemetica` will not be used here).

The website for the docs is still under construction and will be released soon.

**This repository will be always under construction since there are too many interesting things in math that can be shown by code.** Pull requests, issues, questions, and suggestions are all welcomed!

**NB:** I will only maintain the code for `python >= 3.5`.


## Examples

Here is *a very small portion* of examples that this project can do:

+ [Wilson's uniform spanning tree algorithm animation](./src/gifmaze/example_maze_animations.py)

<p align="center">
<a href="https://imgur.com/ptSqlDl"><img src="https://i.imgur.com/ptSqlDl.gif"/></a>
</p>

+ [Hilbert's curve animation](./src/gifmaze/example_hilbert_curve.py)

<p align="center">
<a href="https://imgur.com/gEO7AMR"><img src="https://i.imgur.com/gEO7AMR.gif"/></a>
</p>

+ [Domino shuffling algorithm animation](./src/aztec/run_domino_shuffling_animation.py)

<p align="center">
<a href="https://imgur.com/BWUBjto"><img src="https://i.imgur.com/BWUBjto.gif"/></a>
</p>

+ [Raymarching fractals](./src/fractal3d/fractal3d.py)

<p align="center">
<a href="https://imgur.com/yca2GAj"><img src="https://i.imgur.com/yca2GAj.png" width="600"/></a>
</p>

<p align="center">
<a href="https://imgur.com/Tts3ZUd"><img src="https://i.imgur.com/Tts3ZUd.png" width="600"/></a>
</p>

<p align="center">
<a href="https://imgur.com/O9Q3VOr"><img src="https://i.imgur.com/O9Q3VOr.png" width="600"/></a>
</p>

+ [Hopf fibration](./src/hopf/hopf_fibration.ipynb)

<p align="center">
<a href="https://imgur.com/hJJeone"><img src="https://i.imgur.com/hJJeone.png"/></a>
</p>

+ [Aperiodic tilings](./src/aperiodic-tilings)

<p align="center">
<a href="https://imgur.com/oJ5N06Z"><img src="https://i.imgur.com/oJ5N06Z.png"/></a>
</p>

<p align="center">
<a href="https://imgur.com/oLJQBU2"><img src="https://i.imgur.com/oLJQBU2.png"/></a>
</p>


+ [Langton's ant animation](./src/gifmaze/example_langton_ant.py)

<p align="center">
<a href="https://imgur.com/XwIg4QL"><img src="https://i.imgur.com/XwIg4QL.gif"/></a>
</p>


+ [Reaction-diffusion simulation](./src/grayscott/main.py)

<p align="center">
<a href="https://imgur.com/3dPrFa6"><img src="https://i.imgur.com/3dPrFa6.png" width="600"/></a>
</p>

<p align="center">
<a href="https://imgur.com/3fklRDM"><img src="https://i.imgur.com/3fklRDM.png" width="600"/></a>
</p>

+ [Uniform polytopes](./src/polytopes)

<p align="center">
<a href="https://imgur.com/CpfGucn"><img src="https://i.imgur.com/CpfGucn.png"/></a>
</p>

<p align="center">
<a href="https://imgur.com/pM1gePd"><img src="https://i.imgur.com/pM1gePd.png"/></a>
</p>

<p align="center">
<a href="https://imgur.com/fr69m1j"><img src="https://i.imgur.com/fr69m1j.gif"/></a>
</p>

<p align="center">
<a href="https://imgur.com/qeyPqMZ"><img src="https://imgur.com/qeyPqMZ.png"/></a>
</p>


+ [Uniform tilings](./src/hyperbolic-tilings/example_Euclidean_uniform_tilings.py)

<p align="center">
<a href="https://imgur.com/TFTR5Oo"><img src="https://i.imgur.com/TFTR5Oo.png" width="600"/></a>
</p>

<p align="center">
<a href="https://imgur.com/xbDdPuQ"><img src="https://i.imgur.com/xbDdPuQ.png" width="600"/></a>
</p>



+ [Möbius transformations in hyperbolic 3-space](./src/mobius/Mobius_in_H3space.py)

<p align="center">
<a href="https://imgur.com/U1XgWkc"><img src="https://i.imgur.com/U1XgWkc.png" width="600"/></a>
</p>


## How to use

Each subdirectory in `/src/` is a single program (except that `glslhelpers` is a helper module for running glsl programs and `misc` is a collection of independent scripts), any file named `main.py`, `run_*.py`, `example_*.py` is an executable script that gives some output.


## List of algorithms

Here is a list of some algorithms implemented in this project:

+ [Domino shuffling algorithm](./src/aztec/aztec.py)
+ [Hopcroft's DFA minimization algorithm](./src/hyperbolic-tilings/coxeter/automata.py)
+ [Lempel–Ziv–Welch compression algorithm](./src/gifmaze/gifmaze/encoder.py)
+ [Propp-Wilson's coupling from the past algorithm](./src/cftp/cftp.py)
+ [Todd-Coxeter coset enumeration algorithm](./src/polytopes/todd_coxeter.py)
+ [Wilson's uniform spanning tree algorithm](./src/gifmaze/gifmaze/algorithms.py)
+ [Casselman's minimal roots algorithm](./src/hyperbolic-tilings/coxeter/minroots.py)

## Dependencies

The recommended way to install all dependencies is simply running the script `install_dependencies.sh`.

Or you can install the python libs by pip:

```
pip install -r requirements.txt
```

A few exceptions are: `cairocffi` also requires `libffi-dev` and `pygraphviz` also requires `libgraphviz-dev`:

```
sudo apt-get install libffi-dev libgraphviz-dev
```

Open source softwares:

+ `python3-tk` (for file dialog)
+ `ImageMagick` (for making gif animations)
+ `FFmpeg` (for saving animations to video files)
+ `POV-Ray` (for generating high quality raytracing results)
+ `graphviz` (for drawing automata of Coxeter groups)

They can all be installed via command-line:

```
sudo apt-get install python3-tk imagemagick ffmpeg povray graphviz
```

In the scripts these softwares are called in command line by `povray`, `ffmpeg`, `convert`, etc. For Windows users you should add the directories contain these .exe files to the system `Path` environment variables. For example on Windows the default location of POV-Ray's exe file is `C:\Program Files\POV-Ray\v3.7\bin\pvengine64.exe`, so you should add `C:\Program Files\POV-Ray\v3.7\bin` to system `Path` and rename `pvengine64.exe` to `povray.exe`, then you can run the scripts without any changes and everything works fine.


# Thanks

I have learned a lot from the following people:

- [Bill Casselman](http://www.math.ubc.ca/~cass/)
- [Roice Nelson](https://github.com/roice3)
- [Possibly Wrong](https://possiblywrong.wordpress.com/)
- [Jos Leys](http://www.josleys.com/)


## License

see the LICENSE file.
