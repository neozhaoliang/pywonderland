#!/bin/bash

sudo apt-get install \
     povray \
     ffmpeg \
     imagemagick \
     graphviz \
     python3-tk \
     libgraphviz-dev \
     python3-cairocffi

pip install -r requirements.txt
