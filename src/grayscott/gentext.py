# -*- coding: utf-8 -*_

from PIL import Image, ImageFont, ImageDraw


def generate_text_mask(width, height, text, font_file, fontsize):
    """
    This function helps you generate a black-white image with text
    in it so that it can be used as the mask image in the main program.

    params: 
        width, height: size of the image.
        text: a string to be embedded in the image.
        font_file: path to your .ttf font file.
        fontsize: size of the font.
    """
    img = Image.new('L', (width, height), 'black')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_file, fontsize)
    size_w, size_h = font.getsize(text)
    xy = (width - size_w) // 2, height // 2 - 5 * size_h // 8
    draw.text(xy, text, 'white', font)
    img.save(text + '.png')


if __name__ == '__main__':
    generate_text_mask(480, 320, 'PYTHON', 'ubuntu.ttf', 150)
