# A Tour in the Wonderland of Math with Python


> **A collection of python scripts for drawing beautiful figures and animating interesting algorithms in mathematics**.


## About this repo

The purpose of this project is to show the beauty of math with python by rendering high quality images, videos and animations. It consists of several independent projects with each one illustrates a special object/algorithm in math. The current list contains:

- Aperiodic tilings like Penrose tiling, Ammann-Beenker tiling, etc.
- Triology on perfectly random sampling algorithms.
  1. Domino shuffling algorithm on Aztec diamonds.
  2. Wilson's uniform spanning tree algorithm on 2d grids.
  3. Coupling from the past algorithm on lozenge tilings.
- Hopf fibration.
- 3D and 4D Uniform polytopes.
- 2D uniform tilings and 3D uniform honeycombs in Euclidean, spherical and hyperbolic spaces.
- [Make gif animations of various algorithms](https://github.com/neozhaoliang/pywonderland/blob/master/src/gifmaze).
- Lots of shader animations.
- [Miscellaneous scripts](https://github.com/neozhaoliang/pywonderland/blob/master/src/misc) like E8 root system, Mandelbrot set, Newton's fractal, Lorenz attractor, etc.

These topics are chosen largely due to my personal taste:

1. They must produce appealing results.
2. There must be some non-trivial math behind them.
3. The code should be as simple as possible.

I'll use only popular python libs and build all math stuff by hand (tools like `sage`, `sympy`, `mathemetica` will not be used here).


## Gallery

The code for some of the images are not in the master branch, they can be found in the [released version](https://github.com/neozhaoliang/pywonderland/releases/tag/0.1.0).

+ Uniform 3D and 4D polytopes

<img src="https://user-images.githubusercontent.com/23307174/125021543-77466c00-e0ad-11eb-857a-ca37dd0efe33.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021556-7d3c4d00-e0ad-11eb-81c3-8d8a6ebc8be7.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021561-80373d80-e0ad-11eb-8736-99f0969d657b.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021573-875e4b80-e0ad-11eb-9733-ab01724ecd1f.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021582-8b8a6900-e0ad-11eb-8cd7-49f10f9b4ebf.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021588-8fb68680-e0ad-11eb-86d7-8c3c81016c54.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021753-d7d5a900-e0ad-11eb-94c9-9e2970e5f360.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021760-da380300-e0ad-11eb-9a51-70ddc6662b18.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021765-db693000-e0ad-11eb-9bca-ccd86bee5b82.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021768-dd32f380-e0ad-11eb-967c-a8922bf9f96b.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021772-de642080-e0ad-11eb-9514-59073a0296b6.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021775-defcb700-e0ad-11eb-8c8d-254736a02066.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021924-27b47000-e0ae-11eb-81c7-83231ac19e6b.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021929-2aaf6080-e0ae-11eb-8f9e-3e7976f19df9.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021932-2be08d80-e0ae-11eb-8031-60dd9c8b7589.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021935-2d11ba80-e0ae-11eb-8c53-06539f8cbfab.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021937-2daa5100-e0ae-11eb-8bd0-a9f686eaefeb.png" width="15%"></img> <img src="https://user-images.githubusercontent.com/23307174/125021940-2edb7e00-e0ae-11eb-8221-6b6d1ae2917a.png" width="15%"></img>

<img src="https://user-images.githubusercontent.com/23307174/170702640-74d8bfe7-476d-4581-82e7-f91816d268f6.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/170702831-f34c8040-46df-4ade-a3e7-7e86b298fbc4.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/170703221-229d3e4c-644b-472d-9cdd-e636ade81402.png" width="30%"></img> 

+ Möbius transformations

<img src="https://user-images.githubusercontent.com/23307174/170706652-330f6fff-1e2e-4458-900c-2c96c5269aeb.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/170706658-c11ac2ba-bc8f-4b5c-b1f1-a9e3f339a035.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/170706666-531a3db9-871d-4dac-865d-76c388e89460.png" width="30%"></img> 

<img src="https://user-images.githubusercontent.com/23307174/125022164-a3162180-e0ae-11eb-86f2-d41eaea7ba85.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125022177-a7423f00-e0ae-11eb-9ee8-a711538eda1b.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125022184-a9a49900-e0ae-11eb-9cc7-4c9f9bf126cb.png" width="30%"></img> 

+ Wythoff explorer from [Matt Zucker](https://github.com/mzucker)

<img src="https://user-images.githubusercontent.com/23307174/125022575-9645fd80-e0af-11eb-8494-7a239231b5ce.png" width="45%"></img> <img src="https://user-images.githubusercontent.com/23307174/125022578-98a85780-e0af-11eb-8309-90175066a6be.png" width="45%"></img> 

+ 3D Euclidean uniform honeycombs and their duals

<img src="https://user-images.githubusercontent.com/23307174/125022897-46b40180-e0b0-11eb-9e71-fccfde9f3734.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125022923-529fc380-e0b0-11eb-94ba-bf35a9a9b23c.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125022909-4d427900-e0b0-11eb-9957-1d251fc544d6.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125022914-4e73a600-e0b0-11eb-8946-175b1d3fb71c.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125022922-50d60000-e0b0-11eb-878c-f1d8799ef745.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125022905-4a478880-e0b0-11eb-9ed6-d99b6cd974fa.png" width="30%"></img> 

+ Gray-Scott simulation

<img src="https://user-images.githubusercontent.com/23307174/125023296-22a4f000-e0b1-11eb-9fe2-4f23ae65541e.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125023301-26d10d80-e0b1-11eb-86a2-2d77333fec65.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125023303-29336780-e0b1-11eb-9e85-be678212e7ad.png" width="30%"></img> 


+ 3D hyperbolic uniform honeycombs

<img src="https://user-images.githubusercontent.com/23307174/125023413-7283b700-e0b1-11eb-897e-47c449193535.png" width="45%"></img> <img src="https://user-images.githubusercontent.com/23307174/125023417-744d7a80-e0b1-11eb-85f3-2f0f666fc1b2.png" width="45%"></img> <img src="https://user-images.githubusercontent.com/23307174/125023422-77486b00-e0b1-11eb-91e4-3f161caedc77.png" width="45%"></img> <img src="https://user-images.githubusercontent.com/23307174/125023404-70215d00-e0b1-11eb-9024-bcc79778b6fe.png" width="45%"></img> 

+ Limit set of rank 4 Coxeter groups

<img src="https://user-images.githubusercontent.com/23307174/125023777-2422e800-e0b2-11eb-916a-6b764e434128.png" width="45%"></img> <img src="https://user-images.githubusercontent.com/23307174/125023788-25ecab80-e0b2-11eb-9ff0-e188ee6d86da.png" width="45%"></img> <img src="https://user-images.githubusercontent.com/23307174/125023793-28e79c00-e0b2-11eb-9aa6-a2beaab2004d.png" width="45%"></img> <img src="https://user-images.githubusercontent.com/23307174/125024228-f0948d80-e0b2-11eb-876a-44e65b7d4c4b.png" width="45%"></img>

+ Aperiodic tilings

<img src="https://user-images.githubusercontent.com/23307174/125026199-a9100080-e0b6-11eb-9b08-40c5c1ca2ea1.png" width="45%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026217-b200d200-e0b6-11eb-9c22-4ad68ac9ff1e.png" width="45%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026228-b62cef80-e0b6-11eb-9706-568b08461896.png" width="45%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026248-bdec9400-e0b6-11eb-9ea0-ae2c631e68df.png" width="45%"></img> 

+ 3D Fractals

<img src="https://user-images.githubusercontent.com/23307174/125026554-6b5fa780-e0b7-11eb-99a3-b20f8fc1bf44.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026564-71558880-e0b7-11eb-8bc3-34dcb14514d2.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026568-73b7e280-e0b7-11eb-9377-aff3fa249946.png" width="30%"></img>

+ Coxeter automata and 2D Uniform tilings

<img src="https://user-images.githubusercontent.com/23307174/125031907-cac1b580-e0bf-11eb-8aa3-36ed29e4f40e.png" width="23%"></img> <img src="https://user-images.githubusercontent.com/23307174/125031930-d0b79680-e0bf-11eb-8fd4-b831c71e101a.png" width="23%"></img> <img src="https://user-images.githubusercontent.com/23307174/125031939-d3b28700-e0bf-11eb-88d7-bbd3f3906fec.png" width="23%"></img> <img src="https://user-images.githubusercontent.com/23307174/125031948-d614e100-e0bf-11eb-9e5c-19d9d4999f81.png" width="23%"></img> 
<img src="https://user-images.githubusercontent.com/23307174/125033788-589ea000-e0c2-11eb-9d53-5ce757d0d41b.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125033839-6e13ca00-e0c2-11eb-902f-5394f1fe1cbb.png" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125033855-766c0500-e0c2-11eb-8be4-8d83ae522b9b.png" width="30%"></img>


+ GIF animations of various algorithms

<img src="https://user-images.githubusercontent.com/23307174/125714052-13443b6c-8686-48ba-9d19-b2526d01e034.gif" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125714042-310409c7-10d9-4fae-ac6a-6b7d5ef015dc.gif" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125714045-b873e336-8593-4a17-a549-4319108df44f.gif" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125714051-83a818df-f78c-4bdf-a7d3-55ea183e0a4d.gif" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125714055-c4a90a82-7eb0-4d58-b158-72e860047226.gif" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125714033-9ffea676-26a7-4664-9536-5f8ad4da4cfc.gif" width="30%"></img> <img src="https://user-images.githubusercontent.com/23307174/125714056-21c7c8de-08e9-4ee7-b8f6-fb673d9917dc.gif" width="30%"></img> 

+ Others

<img src="https://user-images.githubusercontent.com/23307174/125026748-cb564e00-e0b7-11eb-82e5-4686f114bd82.png" width="18%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026768-d4dfb600-e0b7-11eb-9e92-3959b86d96f4.png" width="18%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026774-d7421000-e0b7-11eb-8b9a-0ad1d17e1251.png" width="18%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026787-dad59700-e0b7-11eb-889f-b0c737413b6a.png" width="18%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026793-dc9f5a80-e0b7-11eb-9ac7-910bfc6bf81e.png" width="18%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026803-df9a4b00-e0b7-11eb-8764-9277aea9cd53.png" width="18%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026831-ec1ea380-e0b7-11eb-92fd-7e034208d03a.png" width="18%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026859-f5a80b80-e0b7-11eb-8f7c-f2d665680094.png" width="18%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026930-0bb5cc00-e0b8-11eb-91a7-efc3a14489d0.png" width="18%"></img> <img src="https://user-images.githubusercontent.com/23307174/125026938-0eb0bc80-e0b8-11eb-8fed-5d73fc2e21ea.png" width="18%"></img> 

Many more to be comtinued ...

## How to use

All projects here are implemented in a ready-to-use manner for new comers. You can simply run the examples without tweaking any parameters once you have the dependencies installed correctly.

## Dependencies

The recommended way to install all dependencies is simply running the bash script `install_dependencies.sh`.

```
sudo bash install_dependencies.sh
```

Or you can install the python libs by pip:

```
pip install -r requirements.txt
```

Open source softwares required:

+ `python3-tk` (for file dialog)
+ `ImageMagick` (for making gif animations)
+ `FFmpeg` (for saving animations to video files)
+ `POV-Ray` (for generating high quality raytracing results)
+ `graphviz` (for drawing automata of Coxeter groups)
+ `Inkscape` (optional, for convering large svg files to png)

They can all be installed via command-line:

```
sudo apt-get install python3-tk imagemagick ffmpeg povray graphviz inkscape
```


Note `pygraphviz` also requires `libgraphviz-dev`:

```
sudo apt-get install libgraphviz-dev
```

In the scripts these softwares are called in command line as `povray`, `ffmpeg`, `convert` (from `ImageMagick`), etc. For Windows users you should add the directories contain these .exe files to the system `Path` environment variables to let the system know what executables these commands refer to. For example on Windows the default location of POV-Ray's exe file is `C:\Program Files\POV-Ray\v3.7\bin\pvengine64.exe`, so you should add `C:\Program Files\POV-Ray\v3.7\bin` to system `Path` and rename `pvengine64.exe` to `povray.exe`, then you can run the scripts without any changes and everything works fine.

## Thanks

I have learned a lot from the following people:

- [Bill Casselman](http://www.math.ubc.ca/~cass/)
- [Roice Nelson](https://github.com/roice3)
- [Possibly Wrong](https://possiblywrong.wordpress.com/)
- [Jos Leys](http://www.josleys.com/)
- [Greg Egan](http://gregegan.net/)
- [Matthew Arcus](https://github.com/matthewarcus).

## License

see the LICENSE file.
