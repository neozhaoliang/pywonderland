from PIL import Image, ImageFont, ImageDraw


def generate_text_mask(width, height, text, font_file, fontsize):
    img = Image.new('L', (width, height), 'black')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_file, fontsize)
    size_w, size_h = font.getsize(text)
    xy = (width - size_w) // 2, height // 2 - 5 * size_h // 8
    draw.text(xy, text, 'white', font)
    img.save(text + '.png')


generate_text_mask(480, 320, 'PYTHON', 'ubuntu.ttf', 150)
