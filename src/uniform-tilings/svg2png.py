"""
A helper script convert svg files in this directory to png format
"""
import glob
import subprocess
import os


command = "inkscape -z {} -e {}.png"

for svg in glob.glob("*.svg"):
    fname = os.path.basename(svg).split(".")[0]
    subprocess.call(command.format(svg, fname), shell=True)
