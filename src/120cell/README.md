# Render the 120-Cell Polytope with POV-Ray and Vapory

**Note: This is a very coarse version and will be rewritten later.**

Future features will contain:

1. Use Todd - Coxeter algorithm to generate all vertices.
2. A pyglet version of jenn3d to play with various polytopes.
3. POV-Ray rendering of various 4d polytopes.


## About the scene

The scene in the front page contains 3 non-isomorphic generalized Penrose tilings (patterns on the walls and floor) plus the 120-cell, a 4D polytope (projected to 3D of course).

Look at the pattern on the left wall, you can see some "stars" in it, so this is not a standard Penrose tiling. For the pattern on the right wall, it does not contain any stars, but there are "defected star" patterns that also do not occur in standard Penrose tilings, so it's not a Penrose tiling either. **Only the pattern on the floor is the Penrose Tiling.**

## How to use this program

Simply run `python main.py`, nothing else.

This program needs the raytracer `POV-Ray` and the modules `vapory` and `palettable` be installed on your computer. `vapory` is a light wrapper of POV-Ray. Don't be afraid of it, its syntax is almost a plain translation of that of POV-Ray's and you will have no difficulty switching between these two.

`palettable` is used here just for supplying the colors of the Penrose rhombus.

The runtime of this script on my computer is 8 minutes, and I'm sure it will be faster on yours (my computer is an outdated laptop).

## About the code

To understand the code, you need to

+ Know some baics about `POV-Ray`, like its syntax, lights, textures, CSG, ... but you don't need to have a decent knowledge of it (like me).

+ Understand how we drew Penrose tilings in this repo before.

+ Read the wiki page about 120-cell.

+ `Vapory` is handy, try it! 

I know, I know, this script is quite mathematically oriented, may be too hard for other people to understand. You may just enjoy it's beauty!


### Thanks

The data in `cell120.py` is taken from `xscreensaver`. It's a bit (but not too much) tedious to computer these data by oneself, so I just borrowed them. 

Thanks [DeltaSimplex](https://www.youtube.com/user/DeltaSimplex) for teaching me how to set the texture for the faces, and [Zulko](https://github.com/Zulko) for his 
`vapory` module.

