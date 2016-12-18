from struct import pack


# ----------
# constants for the LZW encoding, do not modify these!
PALETTE_BITS = 2
CLEAR_CODE = 4
END_CODE = 5
MAX_CODES = 4096
# ----------
# the usage of this dict will be clear later when performing LZW encoding
color_indices = {'wall_color': '0',
                 'tree_color': '1',
                 'path_color': '2',
                 'paint_color': '3'}
# ----------


def logical_screen_descriptor(width, height):
    '''
    meaning of the packed field 0b10010001,
    read from left (most significant) to right (less significant):
        1: the first bit '1' means there is a global color table.
        2-4: the next 3 bits '001' means that the gif file will show 2**(1+1) = 4
        different colors, these bits are only informational today and modern
        decoders (like eog, firefox and chrome) simply skip them.
        5: the 5th bit '0' is the sort flag and is not used by modern decoders.
        6-8: the last 3 bits indicates the size of the global color table is 2**(1+1) = 4. 
    '''
    return pack('<6s2H3B', b'GIF89a', width, height, 0b10010001, 0, 0)


def global_color_table(palette):
    '''
    this block must follows immediately after the logical screen descriptor.
    '''
    return bytearray(palette)

 
def loop_control_block(loop):
    '''
    this block follows immediately after the global color table.
    '''
    return pack('<3B8s3s2BHB', 0x21, 0xFF, 11, b'NETSCAPE', b'2.0', 3, 1, loop, 0)


def graphics_control_block(delay, trans_index):
    '''
    meaning of the packed field 0b00000101,
    read from left (most significant) to right (less significant):
        1-3: the first 3 bits are not used, they are always 0s.
        4-6: these 3 bits are the disposal method flag. 
             '000' = 0 means 'undefined' action.
             '001' = 1 means leave the last frame in place.
             '010' = 2 means restore to the background color (specified in the global color table)
             '011' = 3 means restore to the last frame.
              4-7 are not defined.
    '''
    return pack("<4BH2B", 0x21, 0xF9, 4, 0b00000101, delay, trans_index, 0)


def image_descriptor(left, top, width, height):
    '''
    each frame contains 3 blocks, they appear in order: 
    1. a graphcs control block that sets the delay and transparent color.
    2. an image descriptor specify the position of the frame.
    3. the virtual lzw-encoded image data.
    '''
    return pack('<B4HB', 0x2C, left, top, width, height, 0)
   

def pad_delay_frame(delay, trans_index):
    '''
    pad a 1x1 pixel transparent frame for delay.
    '''
    control = graphics_control_block(delay, trans_index)
    descriptor = image_descriptor(0, 0, 1, 1)
    data = bytearray([PALETTE_BITS, 1, trans_index, 0])
    return control + descriptor + data



class LZWEncoder(object):

    def __init__(self):
        self.bitstream = bytearray()
        self.num_bits = 0


    def encode_bits(self, num, size):
        '''
        for a given number 'num', encode it as a binary string of
        length size, and pad it at the end of bitstream.

        Example: num = 3, size = 5
        the binary string for 3 is '00011', here we padded extra zeros
        at the left to make its length to be 5.
        The tricky part is that in a gif file, the encoded binary data stream 
        increase from lower (least significant) bits to higher (most significant) bits,
        so we have to reverse it as 11000 and pack this string at the end of bitstream!
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
        Pack the LZW encoded image data into blocks.
        Each block is of length <= 255 and is preceded by a byte
        in 0-255 that indicates the length of this block.

        Note that after calling this method we should reset the encoder.
        '''
        bytestream = bytearray()
        while len(self.bitstream) > 255:
            bytestream += bytearray([255]) + self.bitstream[:255]
            self.bitstream = self.bitstream[255:]
        if self.bitstream:
            bytestream += bytearray([len(self.bitstream)]) + self.bitstream

        self.num_bits = 0
        self.bitstream = bytearray()
        return bytestream


    def __call__(self, input_data, **kwargs):
        code_length = PALETTE_BITS + 1
        next_code = END_CODE + 1

        code_table = {color_indices[key]: index for key, index in kwargs.items()}

        # always start with the clear code
        self.encode_bits(CLEAR_CODE, code_length)

        pattern = str()
        for c in input_data:
            c = str(c)
            pattern += c
            if not pattern in code_table:
                # add new code in the table
                code_table[pattern] = next_code
                # output the prefix to bitstream
                self.encode_bits(code_table[pattern[:-1]], code_length)
                # suffix becomes the current pattern
                pattern = c

                next_code += 1
                if next_code == 2**code_length + 1:
                    code_length += 1
                if next_code == MAX_CODES:
                    next_code = END_CODE + 1
                    self.encode_bits(CLEAR_CODE, code_length)
                    code_length = PALETTE_BITS + 1
                    code_table = {color_indices[key]: index for key, index in kwargs.items()}

        self.encode_bits(code_table[pattern], code_length)
        self.encode_bits(END_CODE, code_length)

        return bytearray([PALETTE_BITS]) + self.dump_bytes() + bytearray([0])

    
lzw_encoder = LZWEncoder()
