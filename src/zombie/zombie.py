'''
Animating zombie cataclysm in America.

Motivated by Brad Pitt's movie "World War Z" and Zulko's blog post:

"http://zulko.github.io/blog/2014/11/29/data-animations-with-python-and-moviepy/"

The model is basically a slightly changed reaction-diffusion process,
the tricky part is how to lay the zombie's density map on top of the
population density map.

The code is not well-structured, since I just want a single animation.
'''
import subprocess
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import convolve
from PIL import Image
from tqdm import tqdm


INFECTION_SPEED = 0.2
TURNING_SPEED = 0.5
DIFFUSION_SPEED = [0, 0.3, 0.12]
KERNEL =  np.array([[0, 1, 0],
                    [1, -4, 1],
                    [0, 1, 0]]) /4.0


def infect(HIZ):
    human, infected, zombie = HIZ
    bitten = INFECTION_SPEED * human * zombie
    turned = TURNING_SPEED * infected
    return np.array([-bitten, bitten-turned, turned])


def conv(mat):
    return convolve(mat, KERNEL, mode='constant', cval=0)


def diffuse(HIZ):
    return np.array([conv(mat) * speed for mat, speed in zip(HIZ, DIFFUSION_SPEED)])


def update(HIZ):
    HIZ += infect(HIZ)
    HIZ += diffuse(HIZ)
    return HIZ


usa_density = Image.open('usa_density.jpg').resize((600, 400))
usa_color = np.array(usa_density).astype(np.float)/255
usa_gray = np.array(usa_density.convert('L')).astype(np.float)/255

HIZ = np.zeros((3,) + usa_gray.shape)
HIZ[0] = usa_gray
HIZ[1, 160, 512] = 1.0
M = np.zeros_like(usa_gray)

days = 280
fig = plt.figure(figsize=(6, 4), dpi=100)
ax = fig.add_axes([0, 0, 1, 1], aspect=1)

for i in tqdm(range(days*24)):
    HIZ = update(HIZ)
    if (i % 24 == 0):
        ax.clear()
        ax.axis("off")
        I, Z = HIZ[1:]
        img = np.dstack((Z**0.1, I**0.2, M, Z**0.2))
        ax.imshow(usa_color, cmap="Greys_r", interpolation="nearest")
        ax.imshow(img, interpolation="nearest")
        fig.savefig("zombie{:03d}.png".format(i/24))


command = ['ffmpeg',
           '-loglevel', 'quiet',
           '-framerate', '16',
           '-i', 'zombie%03d.png',
           '-c:v', 'libvpx',
           '-crf', '20',
           '-b:v', '500k',
           'zombie.webm']

subprocess.check_call(command)
for f in glob.glob('zombie*.png'):
    os.remove(f)
