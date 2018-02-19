# Usage

**Dependency**: this program requires the python lib `cairocffi` and the free software `ImageMagick` be installed on your computer.

1. To sample a random tiling of a Aztec diamond graph of order 100 with uniform probability, run
    ```
    python random_tiling.py -o 100 -s 800 -p matplotlib
    ```
    `-o` is the order of the Aztec diamond, `-s` is the size of the image, `-p` is the program used to draw the image (must be `cairo` or `matplotlib`).

2. To make gif animations of the domino shuffling algorithm, run
    ```
    python domino_shuffling_animation.py -s 400 -o 30
    ```
    Note that windows users need to set the path to your `convert.exe` first.
