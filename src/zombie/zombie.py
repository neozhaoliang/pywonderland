'''
Simulating zombie outbreak in America.
Modified from Zulko's code:

https://gist.github.com/Zulko/6aa898d22e74aa9dafc3

The model is basically a reaction-diffusion process.
I just layed the zombie density map on top of the population density map.

runtime: about 9.5 mins
'''

import subprocess
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.ndimage.filters import convolve
from PIL import Image


def infect(SIR, infection_rate, incubation_rate):
    S, I, R = SIR
    newly_infected = infection_rate * R * S
    newly_rampaging = incubation_rate * I
    dS = - newly_infected
    dI = newly_infected - newly_rampaging
    dR = newly_rampaging
    return np.array([dS, dI, dR])


def disperse(SIR, dispersion_kernel, dispersion_rates):
    return np.array( [convolve(e, dispersion_kernel,
                               mode="constant", cval=0) * r
                      for (e, r) in zip(SIR, dispersion_rates)])


def update(SIR, dt):
    infection = infect(SIR, infection_rate, incubation_rate)
    SIR += dt*infection
    dispersion = disperse(SIR, dispersion_kernel, dispersion_rates)
    SIR += dt*dispersion


usa_density = Image.open('usa_density.jpg').resize((600, 400))
usa_color = np.array(usa_density).astype(np.float)/255
usa_gray = np.array(usa_density.convert('L')).astype(np.float)/255

SIR = np.zeros((3,) + usa_gray.shape)
SIR[0] = usa_gray
SIR[1, 160, 512] = 1.0
M = np.zeros_like(usa_gray)

infection_rate = 0.2
incubation_rate = 0.8
dispersion_rates = [0, 0.3, 0.12]
dispersion_kernel = np.array([[0, 1.0 , 0],
                                [1, -4.0, 1],
                                [0, 1, 0]]) /4.0


days = 280
fig = plt.figure(figsize=(6, 4), dpi=100)
ax = fig.add_axes([0, 0, 1, 1], aspect=1)
dt = 1


for i in tqdm(range(days*24)):
    update(SIR, dt)
    if (i % 24 == 0):
        ax.clear()
        ax.axis("off")
        I, R = SIR[1:]
        img = np.dstack((R**0.1, I**0.2, M, R**0.2))
        plt.imshow(usa_color, cmap="Greys_r", interpolation="nearest")
        plt.imshow(img, interpolation="nearest")
        plt.savefig("zombie{:03d}.png".format(i/24))

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
