"""
A helper script convert svg files in this directory to png format
"""

import glob
import os
import subprocess

command = "inkscape {} -d 300 --export-type='png' --export-filename='{}.png'"

for svg in glob.glob("*.svg"):
    fname = os.path.basename(svg).split(".")[0]
    subprocess.call(command.format(svg, fname), shell=True)
