from struct import pack


# constants for LZW encoding, do not modify these!
PALETTE_BITS = 2
CLEAR_CODE = 4
END_CODE = 5
MAX_CODES = 4096


class DataBlock(object):

    '''
    write bits into bytearrays.
    '''

    def __init__(self):
        # write bits into this array.
        self.bitstream = bytearray()
        # a counter holds how many bit were written.
        self.num_bits = 0


    def encode_bits(self, num, size):
        '''
        given a number 'num', encode it as a binary string of
        length 'size', and pad it at the end of bitstream.
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
        pack the LZW encoded image data into blocks.
        each block is of length <= 255 and is preceded by a byte
        in 0-255 that indicates the length of this block.
        '''
        bytestream = bytearray()
        while len(self.bitstream) > 255:
            bytestream += bytearray([255]) + self.bitstream[:255]
            self.bitstream = self.bitstream[255:]
        if self.bitstream:
            bytestream += bytearray([len(self.bitstream)]) + self.bitstream
        return bytestream



class GIFWriter(object):

    '''
    structure of a gif file: (in the order they appear)

    1. always begins with the logical screen descriptor.
    2. then follows the global color table.
    3. then follows the loop control block (specify the number of loops of the file)
    4. then follows the image data of the frames. each frame is further divided into:
       (i) a graphics control block that specify the delay time and transparent color of the coming frame.
       (ii) the image descriptor for the coming frame.
       (iii) the LZW enconded data of the frame.
    5. finally the trailor '0x3B'.
    '''
    palette = [0, 0, 0,         # wall color
               100, 100, 100,   # tree color
               255, 0, 255,     # path color
               150, 200, 100]   # fill color

    def __init__(self, width, height, loop):
        '''
        these attributes are listed in the order they appear in the file.
        '''
        self.logical_screen_descriptor = pack('<6s2H3B', b'GIF89a', width, height, 0b10010001, 0, 0)
        self.global_color_table = bytearray(self.palette)
        self.loop_control_block = pack('<3B8s3s2BHB', 0x21, 0xFF, 11, b'NETSCAPE', b'2.0', 3, 1, loop, 0)
        self.data = bytearray()
        self.trailor = bytearray([0x3B])


    def graphics_control_block(self, delay, trans_index):
        '''
        this block specifies the delay time and transparent index of the coming frame.
        '''
        return pack("<4BH2B", 0x21, 0xF9, 4, 0b00000101, delay, trans_index, 0)


    def image_descriptor(self, left, top, width, height):
        '''
        this block specifies the region of the coming frame.
        the ending byte field is 0 since we do not need a local color table.
        '''
        return pack('<B4HB', 0x2C, left, top, width, height, 0)


    def pad_delay_frame(self, delay, trans_index):
        '''
        pad a 1x1 pixel image for delay.
        '''
        control = self.graphics_control_block(delay, trans_index)
        descriptor = self.image_descriptor(0, 0, 1, 1)
        data = bytearray([PALETTE_BITS, 1, trans_index, 0])
        return control + descriptor + data


    def save(self, filename):
        '''
        note the 'wb' mode here!
        '''
        with open(filename, 'wb') as f:
            f.write(self.logical_screen_descriptor
                    + self.global_color_table
                    + self.loop_control_block
                    + self.data
                    + self.trailor)


    def LZW_encode(self, input_data, init_table):
        '''
        encode the input image data with LZW algorithm.
        by specifying different initial code tables one can color an image in different ways.

        I think this is the most difficult part and it deserves more explanation.
        In our animation there are 4 possible states of a cell: wall(0), tree(1), path(2), and filled(3).
        in some frames we want to color those walls with black, and in some frames we want to color them transparent,
        so we need a dict to maps the states to the colors (in fact to the indices of the colors in the global color table).

        For example, if we want to color the walls and the tree with 0, i.e. the 0-th color in the global color table,
        color the path with 1 (the 1-th color in the global color table), and color the filled cells with 2,
        we can specify the init_table as follows:

        {'0': 0, '1': 0, '2': 1, '3': 2}

        Now comes the tricky part: when the decoder reads the encoded data, by the standard LZW decoding procedure,
        it will firstly reconstruct the init table always to be

        {'0': 0, '1': 1, '2': 2, '3': 3}

        hmm, not the same with ours ... but the meaning of the keys in the two dicts are different: the key '0' in
        out init table is the state of the cell, whereas the key '0' in the dict the decoder reconstructs is
        the 0-th color in the global color table. so when the decoder sees some 'x' in the encoded stream,
        it really thinks the cell is colored with 'x', this is exactly what we want.
        '''
        stream = DataBlock()

        code_length = PALETTE_BITS + 1
        next_code = END_CODE + 1

        code_table = init_table.copy()

        # always start with the clear code
        stream.encode_bits(CLEAR_CODE, code_length)

        pattern = str()
        for c in input_data:
            c = str(c)
            pattern += c
            if pattern not in code_table:
                # add new code in the table
                code_table[pattern] = next_code
                # output the prefix to bitstream
                stream.encode_bits(code_table[pattern[:-1]], code_length)
                # suffix becomes the current pattern
                pattern = c

                next_code += 1
                # why should we compare with 2 ** code_length + 1 here?
                # hint: the next code you add to code_table will be 2 ** code_length.
                if next_code == 2**code_length + 1:
                    code_length += 1
                if next_code == MAX_CODES:
                    next_code = END_CODE + 1
                    stream.encode_bits(CLEAR_CODE, code_length)
                    code_length = PALETTE_BITS + 1
                    code_table = init_table.copy()

        stream.encode_bits(code_table[pattern], code_length)
        stream.encode_bits(END_CODE, code_length)

        return bytearray([PALETTE_BITS]) + stream.dump_bytes() + bytearray([0])
