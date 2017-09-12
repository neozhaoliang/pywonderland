#!/bin/sh

rm grayscott.mp4

ffmpeg -framerate 24 -i frames/frame%05d.png -c:v libx264 -crf 20 -b:v 2M grayscott.mp4
