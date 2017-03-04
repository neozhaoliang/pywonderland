How to save the animation as a video:

1. set a global variable `count=0` as the counter, and in the function `on_draw()`, write

    ``` python
    if count % 10 == 0:
        pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot{:04d}.png'.format(count // 10))

    count += 1
    ```
    this will take a snapshot at the speed of each 10 frames.
    
2. use ffmpeg to convert the images into a video, for example in commad line, run

    ``` bash
    ffmpeg -loglevel quiet -framerate 10 -i screenshot%04d.png -c:v libvpx -crf 10 -b:v 2M grayscott.webm
    ```



