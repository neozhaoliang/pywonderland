# Usage

1. Install the python lib `pyglet`: `pip install pyglet`.
2. Run 
    ```
    python main.py -size 800x600 -fps 400
    ```
    to play with the simulation, use the `-size` option to set the window size and the `-fps` option to set the fps of the animation. The default is `None`, which means using the maximal possible fps.
3. To use an image to control the growth of the pattern, for example if an image named `test.png` is in current directory, then run
   ```
   python main.py -mask test.png
   ```
4. Press `Ctrl+v` to start saving the animation to a video file and press `Ctrl+v` again to stop saving the video. This requires `ffmpeg` be installed on your computer and can be found on the system path (windows users need to set this path manually).

5. Run
    ```
    python main.py -frate 24 -srate 100
    ```
    to control how the animation is rendered to video. `frate` is the fps of the video (not the animation) and `srate` controls how often a frame is sampled from the animation.
