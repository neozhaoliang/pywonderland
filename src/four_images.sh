#!/bin/sh
echo "There should be no .png files when this script starts..."
ls *.png
python misc/e8.py
python misc/mandelbrot.py
python misc/modulargroup.py
python misc/penrose.py
echo "There should be four .png files when this script ends..."
ls *.png
