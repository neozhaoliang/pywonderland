# Render the 120-Cell Polytope with POV-Ray and Vapory

## How to use this program


This program needs the raytracer `POV-Ray` and the module `vapory` be installed on your computer. Just run `main.py`. It runs much faster than I thought.

If you don't want to run POV - Ray in a python shell, you may wait a few seconds until POV-Ray pops the display window, close it to
kill the process, and run `povray render.ini`. This will restart the rendering in shell.


## About the code

To understand the code, you need to

+ Know some baics about `POV-Ray`, like its syntax, lights, textures, CSG, ... but you don't need to have a decent knowledge of it (like me).

+ Understand how did we draw Penrose tilings in this repo before.

+ Read the wiki page about 120-cell.

+ `Vapory` is handy, try it! 

I know, I know, this script is quite mathematically oriented, may be too hard for other people to understand. You may just enjoy it's beauty!


### Thanks

The data in `cell120.py` is taken from `xscreensaver`. It's a bit (but not too much) tedious to computer these data by oneself, so I just borrowed them. 

Thanks [DeltaSimplex](https://www.youtube.com/user/DeltaSimplex) for teaching me how to set the texture for the faces, and [Zulko](https://github.com/Zulko) for his 
`vapory` module.

