'''
An implementation of the polynomial roots fractal depicted in

http://www.math.ucr.edu/home/baez/roots/

This script takes a rather long time to compute all the roots for d >= 20.
Some experiential runtime for the cases d = 20, 21, 22 on my computer
(a quite out-dated one) are:

d = 20: 19 mins
d = 21: 25 mins
d = 22: 85 mins

I could write it faster, but that would result in a longer code.

'''

from itertools import product
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm



def f(z):
    '''
    Given a complex number z, return a positive real number.
    This function is used for smoothing the heatmap image below.
    '''
    r = z.real*z.real + z.imag*z.imag
    s = min(r, 1/r)
    return s*s*s


def heatmap(size, degree, zoom):
    xmin, xmax, ymin, ymax = zoom
    data = np.ones((size, size), dtype=np.float)
    for poly in tqdm(product(*([[-1, 1]] * degree)), total=2**degree):
        for z in np.roots((1,) + poly):
            x = (size - 1) * (z.real - xmin) / (xmax - xmin)
            y = (size - 1) * (z.imag - ymin) / (ymax - ymin)
            try:
                data[int(y)][int(x)] += f(z)
            except IndexError:
                pass

    return data


def main(size, degree, zoom, filename):
    data = heatmap(size, degree, zoom)
    img = np.log(data) / np.log(np.max(data))
    fig = plt.figure(figsize=(size/100.0, size/100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.imshow(img, cmap='afmhot')
    fig.savefig(filename)


if __name__ == '__main__':
    main(size=800,
         degree=22,
         zoom=[-1.6, 1.6, -1.6, 1.6],
         filename='rootsart.png')
