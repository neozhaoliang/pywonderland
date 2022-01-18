#!/bin/bash

sudo apt-get install \
     povray \
     ffmpeg \
     imagemagick \
     graphviz \
     libgraphviz-dev \
     python3-cairocffi \
     inkscape

sudo pip3 install -r requirements.txt
