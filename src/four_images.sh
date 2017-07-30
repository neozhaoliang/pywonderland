#!/bin/sh
echo "There should be no .png files when this script starts."
ls *.png
echo "Running four pywonderland scripts..."
python misc/e8.py
python misc/mandelbrot.py
python misc/modulargroup.py
python misc/penrose.py
echo "There should be four .png files when this script ends."
ls *.png
echo "Copying all .png files to the shared directory."
cp *.png /data_to_host
