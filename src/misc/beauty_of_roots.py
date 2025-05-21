"""
~~~~~~~~~~~~~~~
Beauty of Roots
~~~~~~~~~~~~~~~

Reproduce the image from

    https://math.ucr.edu/home/baez/roots/

I don't know the actual color scheme Sam Derbyshire used. I tried many experiments to
make the output image as close as possible to Sam Derbyshire's. Initially, I used
matplotlib's `afmhot` colormap. Although its style was similar to Sam Derbyshire's
result, the overall aesthetic was not satisfactory. Eventually, I found that using a
custom colormap produced better results. The downside of this approach is that when
you change the image resolution, you also need to adjust the polynomial degree and the
color palette accordingly. The code below works best with height = 800.
"""

import numpy as np
import tqdm
from itertools import product
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

degree = 24
width, height = 1000, 800
img = np.zeros((height, width), dtype=int)

x_max = 2
x_min = -2
y_max = 1.6
y_min = -1.6

for deg in range(1, degree + 1):
    print(f"degree={deg}")
    for poly in tqdm.tqdm(product(*([[-1, 1]] * deg)), total=2**deg, unit=" polys"):
        for z in np.roots((1,) + poly):
            x = (width - 1) * (z.real - x_min) / (x_max - x_min)
            y = (height - 1) * (z.imag - y_min) / (y_max - y_min)
            if 0 <= x <= width - 1 and 0 <= y <= height - 1:
                img[int(y)][int(x)] += 1

colors = [
    (0.0, (0, 0, 0)),
    (0.2, (0.01, 0, 0)),
    (0.3, (0.05, 0, 0)),
    (0.4, (0.1, 0.0, 0)),
    (0.5, (0.375, 0.0, 0)),
    (0.56, (0.778, 0.15, 0)),
    (0.61, (1.0, 0.647, 0.2)),
    (0.64, (1, 1, 1)),
    (0.65, (1, 1, 1)),
    (1.0, (1.0, 1.0, 1.0)),
]
# save the result so that you can tweak the color scheme without recomputing the image
np.save("polyroots.npy", img)
img = np.load("polyroots.npy").astype(float)
img = np.log2(img + 1) / np.log2(np.amax(img) + 1)
cmap = LinearSegmentedColormap.from_list("hot_glow", colors)
plt.imsave("polyroots.png", img, cmap=cmap)
