# How to use this program


I found it hard to program buttons and menus in pyglet, so let this be a command line version.


## Keyboard and mouse interface:

You may use your mouse to draw on the screen at any stage.

 
1. run `python main.py` or `python3 main.py` you will see the simulation run in a window popped by pyglet.

2. to change to another pattern, press keyboard 's' (short for 'species').

3. to color it another way, press 'p' (short for 'palette').

4. to save a screenshot, press 'enter'.

5. to save current config into a json file, press 'ctrl + s' (short for 'save').

6. to load a favorable config from the json file, press 'ctrl + o' (short for 'open'). enter the line number of the config you chose and then draw on the blank screen to see the pattern.

7. press 'esc' to close the window.


I have pre-computed some configs in the `palette.json` file.

## How to save the animation as a video:

1. set a global variable `count=0` as the counter, and in the function `on_draw()`, write

    ``` python
    if count % 10 == 0:
        pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot{:04d}.png'.format(count // 10))

    count += 1
    ```
    this will take a screenshot every 10 frames.
    
2. use ffmpeg to convert the images into a video, for example run command line

    ``` bash
    ffmpeg -loglevel quiet -framerate 10 -i screenshot%04d.png -c:v libvpx -crf 10 -b:v 2M grayscott.webm
    ```
    the -framerate specifies the number of frames persecond, -b:v specifies the bitrate(the higher the better quality but larger file)	


