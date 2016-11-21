from struct import pack


__all__ = ['logical_screen_descriptor',
           'global_color_table',
           'loop_control_block',
           'graphics_control_block',
           'image_descriptor',
           'lzw_encoder',
           'PALETTE_BITS']



# Constants for LZW encoding
# Do not modify these!
# --------
PALETTE_BITS = 2
CLEAR_CODE = 4
END_CODE = 5
MAX_CODES = 4096
# --------


def logical_screen_descriptor(width, height):
    '''
    This block always follows the gif header 'GIF89a' immediately.
    '''
    return pack('<2H3B', width, height, 0b10010001, 0, 0)


def global_color_table(*color_list):
    '''
    This block always follows the logical screen descriptor immediately.
    '''
    palette = []
    for color in color_list:
        palette.extend(color)
    return pack('{:d}B'.format(len(palette)), *palette);


def loop_control_block():
    '''
    This block may occur anywhere in a gif image,
    it only affects the frames after it
    until a next loop control block.
    '''
    return pack('<3B8s3s2BHB', 0x21, 0xFF, 11, 'NETSCAPE', '2.0', 3, 1, 0, 0)


def graphics_control_block(delay):
    '''
    This block should occur just before the image descriptor block,
    it only controls the single frame that follows it.
    '''
    return pack("<4BH2B", 0x21, 0xF9, 4, 0b00000101, delay, 3, 0)


def image_descriptor(left, top, width, height):
    '''
    the packing field (the last byte) is always 0,
    since we do not need any local color table here.
    '''
    return pack('<B4HB', 0x2C, left, top, width, height, 0)




class LZWEncoder(object):

    def __init__(self):
        self.bitstream = bytearray()
        self.num_bits = 0


    def encode_bits(self, num, size):
        '''
        for a given number 'num', encode it as a binary string of
        length size, and pad it at the end of bitstream.

        Example:    num = 3, size = 5
        the binary string for 3 is '00011', here we padded extra zeros
        at the left to make its length to be 5.
        The tricky part is that in a gif file, the binary data stream increase
        from lower (least significant) bits to higher (most significant) bits, so
        we should reverse it as 11000 and append this string at the end of bitstream!
        '''
        string = bin(num)[2:].zfill(size)
        for digit in reversed(string):
            if len(self.bitstream) * 8 == self.num_bits:
                self.bitstream.append(0)
            if digit == '1':
                self.bitstream[-1] |= 1 << self.num_bits % 8
            self.num_bits += 1


    def dump_bytes(self):
        '''
        Split the LZW encoded image data into blocks.
        Each block is of length <= 255 and is preceded by a byte
        in 0-255 that indicates the length of this block.

        Note that after calling this method we should reset the attributes to their
        initial states.
        '''
        bytestream = str()
        while len(self.bitstream) > 255:
            bytestream += chr(255) + self.bitstream[:255]
            self.bitstream = self.bitstream[255:]
        if self.bitstream:
            bytestream += chr(len(self.bitstream)) + self.bitstream

        self.reset()
        return bytestream


    def __call__(self, imagedata, *color_indexes):
        '''
        Now comes the most difficult part of code in this script!
        the imagedata should be a 1D array of integers in [0, 1, 2, 3],
        the length of color_indexes must be as least as the different numbers in imagedata.

        The first color in color_indexes is used to paint the pixels with value 0,
        the second color in color_indexes is used to paint the pixels with value 1, ... and so on.
        So if you only specify two colors in the color_indexes but the imagedata contains at least 3
        different numbers in [0, 1, 2, 3], you would get an error.
        '''
        code_length = PALETTE_BITS + 1
        next_code = END_CODE + 1

        # The following line is much deeper than it's first-look,
        # Make sure you understand it!
        code_table = {str(i): c for i, c in enumerate(color_indexes)}

        # Always start with the clear code
        self.encode_bits(CLEAR_CODE, code_length)

        pattern = str()
        for c in map(str, imagedata):
            pattern += c
            if not pattern in code_table:
                # add new code in the table
                code_table[pattern] = next_code
                # output the prefix to bitstream
                self.encode_bits(code_table[pattern[:-1]], code_length)
                # suffix becomes the current pattern
                pattern = c

                next_code += 1
                # this is also a tricky part here: why should we compare with 2**code_length + 1?
                # hint: if next_code == 2**code_length + 1 then the next time the code you write to
                # bitstream would be 2**code_length :P
                if next_code == 2**code_length + 1:
                    code_length += 1
                if next_code == MAX_CODES:
                    next_code = END_CODE + 1
                    self.encode_bits(CLEAR_CODE, code_length)
                    code_length = PALETTE_BITS + 1
                    code_table = {str(i): c for i, c in enumerate(color_indexes)}

        self.encode_bits(code_table[pattern], code_length)
        self.encode_bits(END_CODE, code_length)

        return chr(PALETTE_BITS) + self.dump_bytes() + chr(0)

    def reset(self):
        self.num_bits = 0
        self.bitstream = bytearray()


lzw_encoder = LZWEncoder()
