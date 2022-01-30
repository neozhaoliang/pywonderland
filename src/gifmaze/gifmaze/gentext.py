from PIL import Image, ImageDraw, ImageFont


def generate_text_mask(size, text, fontfile, fontsize):
    """
    This function helps you generate a black-white image with text
    in it so that it can be used as the mask image in the program.
    The black pixels are considered as 'blocked' and white pixels
    are considered as 'connective'.

    Important: this mask must preserve the connectivity of the graph,
    otherwise the program will not terminate.

    :param size: size of the image.
    :param text: a string to be embedded in the image.
    :param fontfile: path to your .ttf font file.
    :param fontsize: size of the font.
    """
    img = Image.new("L", size, "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(fontfile, fontsize)
    size_w, size_h = font.getsize(text)
    xy = (size[0] - size_w) // 2, size[1] // 2 - 5 * size_h // 8
    draw.text(xy, text, "black", font)
    return img
