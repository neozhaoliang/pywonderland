# Generalized Penrose Tilings

This program renders generalized Penrose tilings using de Bruijn's penragrid method.

**Requirements**:

1. `numpy` and `cairocffi` for the 2D drawing with python.
2. The free raytracer `POV-Ray` for rendering the 3D scene.


## Usage

Firstly run

```
python penrose_debruijn.py
```

This will output a .png image of a generalized Penrose tiling rendered by `cairo` and a POV-Ray include file `rhombus.inc` that contains the data of the rhombus, then go to the folder `/povray` and run the file `scene.pov` with `POV-Ray`, for example in command line:

```
povray scene.pov +W800 +H600 +Q11 +A0.001 +R5
```

One can also use `ImageMagick` to add some shading effect on the 2D image rendered by cairo:

```
convert penrose_debruijn.png +shade 20x20 -modulate 250 penrose_debruijn.png
```

**Reference**:

> Algebraic theory of Penrose's non-periodic tilings of the plane. N.G.de Bruijn.
