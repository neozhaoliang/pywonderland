"""
This script reproduces the scene of 120-cell in the movie

"Dimensions - A walk through mathematics"

at "http://www.dimensions-math.org/".

The rendering may take 3~4 days to complete.

:copyright (c) 2018 by Zhao Liang.
"""
import os
import subprocess
from models import Polychora
import helpers


POVRAY_EXE = "povray"  # POV-Ray exe binary
SCENE_FILE = "dimensions_movie.pov"  # the main scene file
OUTPUT_DIR = "./frames/"  # output directory
FRAMES = 1200  # number of frames
IMAGE_SIZE = 600  # image size in pixels
IMAGE_QUALITY_LEVEL = 11  # between 0-11
SUPER_SAMPLING_LEVEL = 5  # between 1-9
ANTIALIASING_LEVEL = 0.001 # lower for better quality

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

POV_COMMAND = "cd povray && " + \
              POVRAY_EXE + \
              " +I{}".format(SCENE_FILE) + \
              " +W{}".format(IMAGE_SIZE) + \
              " +H{}".format(IMAGE_SIZE) + \
              " +Q{}".format(IMAGE_QUALITY_LEVEL) + \
              " +A{}".format(ANTIALIASING_LEVEL) + \
              " +R{}".format(SUPER_SAMPLING_LEVEL) + \
              " +KFI0" + \
              " +KFF{}".format(FRAMES - 1) + \
              " +O../{}".format(OUTPUT_DIR)


def main():
    coxeter_diagram = (5, 2, 2, 3, 2, 3)
    coxeter_matrix = helpers.fill_matrix(coxeter_diagram)
    mirrors = helpers.get_mirrors(coxeter_diagram)
    P = Polychora(coxeter_matrix, mirrors, (1, 0, 0, 0))
    P.build_geometry()
    P.export_pov("./povray/120-cell-data.inc")
    subprocess.call(POV_COMMAND, shell=True)


if __name__ == "__main__":
    main()
