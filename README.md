# A Tour in the Wonderland of Math with Python

> A collection of python scripts for drawing beautiful figures or animating interesting algorithms in mathematics.


## About this repo

Math is beautiful, but to truly enjoy it one has to walk a long and painful way learning lots of boring stuff before he could see the full landscape. I hope this repo could help those people without a strong math background get some intuitive understanding of the beauty and elegance of math. The topics are chosen largely due to my personal taste:

1. They must produce appealing results.
2. There must be some non-trivial math behind them.
3. The code should be as simple as possible.

I'll use only popular python libs and build all math stuff by hand (tools like `sage`, `sympy`, `mathemetica` will not be used here).

The website for the docs is still under construction and will be released soon.

**This repository will be always under construction since there are too many interesting things in math that can be shown by code.** Pull requests, issues, questions, and suggestions are all welcomed!

**NB:** I will only maintain the code for `python >= 3.5`.


## Programs to come:

- Fractals with orbit trap
- 2D hyperbolic tilings (Escher's circle limit)
- 3D hyperbolic honeycombs
- Knots
- Hopf fibration
- Minimal surfaces


## Dependencies

Python libs: you can install almost all the libs by running

```
pip install -r requirements.txt
```

the only exception is `cairocffi` which also requires `libffi-dev`:

```
sudo apt-get install libffi-dev
```

Open source softwares:

+ `ImageMagick` (for making gifs and some post-processing)
+ `FFmpeg` (for saving animations into video files)
+ `POV-Ray` (for generating high quality ray-tracing results)
+ `graphviz` (for drawing automata of Coxeter groups)

They can all be installed via command-line:

```
sudo apt-get install imagemagick ffmpeg povray graphviz
```

# Thanks

I have learned a lot from the following people:

- [Bill Casselman](http://www.math.ubc.ca/~cass/)
- [Roice Nelson](https://github.com/roice3)
- [Possibly Wrong](https://possiblywrong.wordpress.com/)
- [Jos Leys](http://www.josleys.com/)


## License

see the LICENSE file.
