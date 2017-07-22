# Reaction-Diffusion Simulation with Pyglet and GLSL.

This program is motivated by [pmneila's Javascript project](http://pmneila.github.io/jsexp/grayscott/). Run `main.py` to play with the simulation.


## Keyboard and mouse interface:


+ Press `s` (short for "species") to change to another pattern.

+ Press `p` (short for "palette") to color the pattern another way.

+ Press `Enter` to save a screenshot.

+ Press `Ctrl` + `s` (short for "save") to save current config to a json file.

+ Press `Ctrl` + `o` (short for "open") to load a favorable config from the json file. Enter the line number of the config then it will be loaded. The screen might become blank, just draw on it.

+ Press `Ctrl` + `r` to restore to default config.
+ press `Esc` to close the window.

I put some configs in the `palette.json` file. Do have a try!


## How to save the animation to a video:

1. Set a global variable `count=0` as the counter, and in the function `on_draw()`, write

    ``` python
    global count
    if count % 10 == 0:
        pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot{:04d}.png'.format(count // 10))

    count += 1
    ```
    This will take a screenshot every 10 frames.
    
2. Use ffmpeg to convert the images into a video. For example to make a `.webm` video run command line

    ``` bash
    ffmpeg -loglevel quiet -framerate 10 -i screenshot%04d.png -c:v libvpx -crf 10 -b:v 2M grayscott.webm
    ```
    `-i screenshot%04d.png` specifies the images files, `-framerate` specifies the number of frames persecond, `-c:v libvpx` is the encoder, `-b:v` specifies the bitrate (the higher the better quality but larger file).	


## About the code

`pyglet.gl` is only a thin wrapper of `OpenGL`, so one has to write his own helper classes to manage things like `vbo`, `vao`, `shader`, `fbo`, etc. There are some modules like `vispy` and `gletools` that do this job, but that lays the burden of learning one more package.

I wrote two helper classes `shader.py` (adapted from other people's work) and `framebuffer.py`. They are not meant to be serious tools, just kept simple and suffice for our work.

The GLSL code borrows heavily from pmneila's work, the most genius part in his code (and also the most tricky thing if you want to understand the code) is the use of a `brush` variable as the interface between the shader and the mouse.

I found it hard to program buttons and menus in pyglet, so let this be a command line version, pardon me with this.
