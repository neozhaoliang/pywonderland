# Dockerfile for pywonderland
# Usage: docker build -t pywonderland .

FROM python:3

LABEL "repo"="https://github.com/neozhaoliang/pywonderland"

WORKDIR /usr/src/app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update \
 && apt-get upgrade --yes \
 && apt-get install libcairo2-dev ImageMagick povray --yes \
 && pip install cairocffi numpy matplotlib palettable pillow pyglet scipy tqdm vapory \
 && echo "Starting of numba... (get a coffee)" \
 && pip install numba \
 && echo "=================================================================" \
 && echo "Please type: docker run -it --rm --name pywonderland pywonderland"

CMD [ "bash" ]
# CMD [ "python", "./src/misc/mandelbrot.py"]
