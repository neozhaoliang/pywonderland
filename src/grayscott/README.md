# Reaction - Diffusion simulation with Python and glsl

This project is motivated by [pmneila's javascript project](http://pmneila.github.io/jsexp/grayscott/). The core part of the code are the two glsl shaders `reaction.frag` and `render.frag`. The python scripts are merely for creating the UI and compiling and communicating with the glsl code.

**Requirements**:

1. `pyglet` for the UI and OpenGL environment.
2. `ffmpeg` for writing the animation to .mp4 videos.
3. The version of the glsl code is 130.


## Usage

You may simply run `python grayscott.py` to play with the simulation (for keyboard and mouse control please see the printed doc), or add more options like

```bash
python grayscott.py -size 600x480 -conf 1 -scale 2 -fps 400
```

where `-size` is the size of the window, `-conf` is the line number of the pattern that the program will load from the file `config.txt` (which contains a few precomputed patterns), `-scale` controls the "resolution" of the texture, `-fps` is the frames per second of the animtion.

You may also use an image file to control the growth of the pattern by adding the `-mask` option:

```bash
python grayscott.py -mask image.png
```

## How to save the animation to a video file

Firstly make sure `ffmpeg` is installed on your computer and can be found on system path, windows users need to add the path to your `ffmpeg.exe` to system `PATH` variables, then press `Ctrl+v` to start rendering the animation to a .mp4 video and press `Ctrl+v` again to stop the rendering.

You can use the option `-videorate` to control the frames per second of the video (not the animation!) and the option `-samplerate` to control how often a frame is sampled from the animation. If the frames are sampled too frequently then the size of the video file will grow very large.


## Abou the code

`pyglet` is only a thin wrapper of OpenGL so one has to write his own classes to manage things like `vao`, `vbo`, `framebuffer`, etc. There are some modules like `vispy` and `gletools` that do this job, but that lays the burden of learning one more package.

I wrote two scripts `shader.py` and `framebuffer.py` for compiling the shader programs and rendering to texture. They are not meant to be serious tools, just kept simple and suffice for our work.

The glsl code borrows heavily from pmneila's work, the most genius part in his code is the use of a "brush" variable (`u_mouse` in our program) as the interface between the shader and the UI.
