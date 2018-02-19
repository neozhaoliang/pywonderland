# Usage

1. Make sure the python lib `cairocffi` is installed, you can install it via pip
    ```bash
    pip install cairocffi
    ```
    
2. Make sure the free raytracer `POV-Ray` is installed on your computer.

3. Run `python penrose.py`, this will produce an `.png` image (drawn by `cairo`) and a `.pov` file `rhombus.pov`.

4. Run `render.ini` with `POV-Ray`, this will render the 3D image of the tiling.