# Dockerfile for pywonderland
# Usage: docker build -t pywonderland .

FROM python:3

LABEL "repo"="https://github.com/neozhaoliang/pywonderland"

WORKDIR /usr/src/app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get clean \
 && apt-get update \
 && apt-get upgrade --yes \
 && apt-get install libcairo2-dev ImageMagick povray --yes \
 && pip install cffi==1.7.0 cairocffi numpy matplotlib palettable pillow pyglet scipy tqdm vapory \
 && echo "Starting of numba... (get a coffee)" \
 && pip install numba \
 && echo "=====================================================================================================" \
 && echo "Please type: docker run -it -v ~/data_from_docker:/data_to_host --rm --name pywonderland pywonderland"

CMD [ "bash" ]
# CMD [ "source", "four_images.sh"]
