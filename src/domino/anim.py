import os
import glob
import subprocess
import argparse
from PIL import Image
import aztec


CONVERTER = 'convert'


def make_animation(order, size, filename, delay=15):
    '''
    Render one frame for each step in the algorithm
    '''
    az = aztec.AzGraph(0)
    for i in range(order):
        az.delete()
        az.render(size, order + 1, '_tmp{:03d}.png'.format(3 * i))

        az = az.slide()
        az.render(size, order + 1, '_tmp{:03d}.png'.format(3 * i + 1))

        az.create()
        az.render(size, order + 1, '_tmp{:03d}.png'.format(3 * i + 2))

    # pad some frames at the end
    im = Image.open('_tmp{:03d}.png'.format(3 * order - 1))
    for i in range(30):
        im.save('_tmp{:03d}.png'.format(3 * order + i))

    delay = str(int(delay))
    command = [CONVERTER,
               '-delay', delay,
               '-layers', 'Optimize',
               '_tmp*.png',
               filename]
    subprocess.check_call(command)

    # do the clean up
    for f in glob.glob('_tmp*.png'):
        os.remove(f)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-order', metavar='o', type=int, default=30,
                        help='order of aztec diamond')
    parser.add_argument('-size', metavar='s', type=int, default=400,
                        help='image size')
    parser.add_argument('-filename', metavar='f', default='dominoshuffling.gif',
                        help='output filename')
    args = parser.parse_args()
    make_animation(args.order, args.size, args.filename)


if __name__ == '__main__':
    main()
