#!/bin/sh

convert -delay 5 -layers Optimize frames/*.png grayscott.gif

convert grayscott.gif \( +clone -set delay 300 \) +swap +delete grayscott.gif
