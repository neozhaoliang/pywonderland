'''
A kaleidoscope pattern with icosahedral symmetry.
'''
import numpy as np
from PIL import Image
from matplotlib.colors import hsv_to_rgb


def Klein(z):
    '''Klein's j-function'''
    return 1728 * (z * (z**10 + 11 * z**5 - 1))**5 / \
        (-(z**20 + 1) + 228 * (z**15 - z**5) - 494 * z**10)**3


def RiemannSphere(z):
    '''
    map the complex plane to Riemann's sphere via stereographic projection
    '''
    t = 1 + z.real*z.real + z.imag*z.imag
    return 2*z.real/t, 2*z.imag/t, 2/t-1


def Mobius(z):
    '''
    distort the result image by a mobius transformation
    '''
    return (z - 20)/(3*z + 1j)


def render(z):
    z = RiemannSphere(Klein(Mobius(Klein(z))))

    # define colors in hsv space
    H = np.sin(z[0]*np.pi)**2
    S = np.cos(z[1]*np.pi)**2
    V = abs(np.sin(z[2]*np.pi) * np.cos(z[2]*np.pi))**0.2
    HSV = np.dstack((H, S, V))

    # transform to rgb space
    img = hsv_to_rgb(HSV)
    Image.fromarray(np.uint8(img*255)).save('kaleidoscope.png')


def main(imgsize):
    x = np.linspace(-6, 6, imgsize)
    y = np.linspace(6, -6, imgsize)
    z = x[None, :] + y[:, None]*1j
    render(z)


if __name__ == '__main__':
    import time
    start = time.time()
    main(imgsize=800)
    end = time.time()
    print('runtime: {:3f} seconds'.format(end - start))
