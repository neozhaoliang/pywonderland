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

The purpose of this project is to show the beauty of math with python. It consists of several independent sub-projects. The topics are chosen largely due to my personal taste:

1. They must produce appealing results.
2. There must be some non-trivial math behind them.
3. The code should be as simple as possible.

I'll use only popular python libs and build all math stuff by hand (tools like `sage`, `sympy`, `mathemetica` will not be used here). Also I only maintain the code for `python >= 3.6`.

**Note**: Python3.5 is deprecated now because it's a bit tricky to install latest numba on Ubuntu for python3.5.

The website for the docs is still under construction and will be released soon.

A few examples:

<p align="center">
<img src="./gallery.png" width="800">
</p>


## How to use

Each subdirectory in `/src/` is a single program (except that `glslhelpers` is a helper module for running glsl programs and `misc` is a collection of independent scripts), any file named `main.py`, `run_*.py`, `example_*.py` is an executable script that gives some output.


## List of algorithms

Here is a list of some algorithms implemented in this project:

+ [Domino shuffling algorithm](./src/aztec/aztec.py)
+ [Hopcroft's DFA minimization algorithm](./src/uniform-tilings/coxeter/automata.py)
+ [Lempel–Ziv–Welch compression algorithm](./src/gifmaze/gifmaze/encoder.py)
+ [Propp-Wilson's coupling from the past algorithm](./src/cftp/cftp.py)
+ [Todd-Coxeter coset enumeration algorithm](./src/polytopes/todd_coxeter.py)
+ [Wilson's uniform spanning tree algorithm](./src/gifmaze/gifmaze/algorithms.py)
+ [Casselman's minimal roots algorithm](./src/uniform-tilings/coxeter/reftable.py)
+ [Encoding and decoding algorithms for Gray code](./src/gifmaze/example_hilbert_curve.py)

## Dependencies

The recommended way to install all dependencies is simply running the script `install_dependencies.sh`.

Or you can install the python libs by pip:

```
pip install -r requirements.txt
```

Note `pygraphviz` also requires `libgraphviz-dev`:

```
sudo apt-get install libgraphviz-dev
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
