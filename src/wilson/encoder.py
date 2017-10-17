from struct import pack


class DataBlock(object):
    """Write bits into a bytearray and then pack this bytearray into data blocks.
    This class is used in the LZW algorithm when encoding maze into frames."""

    def __init__(self):
        self._bitstream = bytearray()  # write bits into this array.
        self._nbits = 0  # a counter holds how many bits have been written.

    def encode_bits(self, num, size):
        """Given a number `num`, encode it as a binary string of length `size`,
        and pack it at the end of bitstream.
        Example: num = 3, size = 5. The binary string for 3 is '00011',
        here we padded extra zeros at the left to make its length to be 5.
        The tricky part is that in a gif file, the encoded binary data stream
        increase from lower (least significant) bits to higher
        (most significant) bits, so we have to reverse it as '11000' and pack
        this string at the end of bitstream!
        """
        string = bin(num)[2:].zfill(size)
        for digit in reversed(string):
            if len(self._bitstream) * 8 == self._nbits:
                self._bitstream.append(0)
            if digit == '1':
                self._bitstream[-1] |= 1 << self._nbits % 8
            self._nbits += 1

    def dump_bytes(self):
        """Pack the LZW encoded image data into blocks.
        Each block is of length <= 255 and is preceded by a byte
        in 0-255 that indicates the length of this block.
        """
        bytestream = bytearray()
        while len(self._bitstream) > 255:
            bytestream += bytearray([255]) + self._bitstream[:255]
            self._bitstream = self._bitstream[255:]
        if len(self._bitstream) > 0:
            bytestream += bytearray([len(self._bitstream)]) + self._bitstream

        self._nbits = 0
        self._bitstream = bytearray()
        return bytestream


stream = DataBlock()


class GIFWriter(object):
    """
    Structure of a GIF file: (in the order they appear)
    1. always begins with the logical screen descriptor.
    2. then follows the global color table.
    3. then follows the loop control block (specify the number of loops)
    4. then follows the image data of the frames, each frame is further divided into:
       (i) a graphics control block that specify the delay and transparent color of this frame.
       (ii) the image descriptor.
       (iii) the LZW enconded data.
    5. finally the trailor '0x3B'.
    """

    def __init__(self, width, height, min_bits, palette, loop):
        """Attributes are listed in the order they appear in the GIF file."""
        # constants for LZW encoding.
        self._palette_bits = min_bits
        self._clear_code = 1 << min_bits
        self._end_code = (1 << min_bits) + 1
        self._max_codes = 4096

        packed_byte = 1  # the packed byte in the logical screen descriptor.
        packed_byte = packed_byte << 3 | (self._palette_bits - 1)  # color resolution.
        packed_byte = packed_byte << 1 | 0                         # sorted flag.
        packed_byte = packed_byte << 3 | (self._palette_bits - 1)  # size of the global color table.
        self.logical_screen_descriptor = pack('<6s2H3B', b'GIF89a', width, height, packed_byte, 0, 0)

        valid_len = 3 * (1 << min_bits)
        if len(palette) > valid_len:
            palette = palette[:valid_len]
        if len(palette) < valid_len:
            palette += [0] * (valid_len - len(palette))
        self.global_color_table = bytearray(palette)

        self.loop_control = pack('<3B8s3s2BHB', 0x21, 0xFF, 11, b'NETSCAPE', b'2.0', 3, 1, loop, 0)
        self.data = bytearray()
        self.trailor = bytearray([0x3B])

    @staticmethod
    def graphics_control_block(delay, trans_index):
        """This block specifies the delay and transparent color of a frame."""
        return pack("<4BH2B", 0x21, 0xF9, 4, 0b00000101, delay, trans_index, 0)

    @staticmethod
    def image_descriptor(left, top, width, height):
        """This block specifies the position of a frame (relative to the window).
        The ending packed byte field is 0 since we do not need a local color table."""
        return pack('<B4HB', 0x2C, left, top, width, height, 0)

    def pad_delay_frame(self, delay, trans_index):
        """Pad a 1x1 pixel frame for delay. The image data could be written as
        `bytearray([self._palette_bits, 1, trans_index, 0])`, this works fine for decoders
        like firefox and chrome but fails for some decoders like eye of gnome
        when `self._palette_bits` is 7 or 8. Using the LZW encoding is a bit tedious but it's
        safe for all possible values of `self._palette_bits` (1-8) and all decoders.
        """
        control = self.graphics_control_block(delay, trans_index)
        descriptor = self.image_descriptor(0, 0, 1, 1)
        code_length = self._palette_bits + 1
        stream.encode_bits(self._clear_code, code_length)
        stream.encode_bits(trans_index, code_length)
        stream.encode_bits(self._end_code, code_length)
        data = bytearray([self._palette_bits]) + stream.dump_bytes() + bytearray([0])
        return control + descriptor + data

    def LZW_encode(self, input_data):
        """Implement the LZW-encoding algorithm for GIF specification."""
        code_length = self._palette_bits + 1
        next_code = self._end_code + 1
        code_table = {(i,): i for i in range(1 << self._palette_bits)}
        stream.encode_bits(self._clear_code, code_length)  # always start with the clear code.

        pattern = tuple()
        for c in input_data:
            pattern += (c,)
            if pattern not in code_table:
                code_table[pattern] = next_code  # add new code in the table.
                stream.encode_bits(code_table[pattern[:-1]], code_length)  # output the prefix.
                pattern = (c,)  # suffix becomes the current pattern.

                next_code += 1
                if next_code == 2**code_length + 1:
                    code_length += 1
                if next_code == self._max_codes:
                    next_code = self._end_code + 1
                    stream.encode_bits(self._clear_code, code_length)
                    code_length = self._palette_bits + 1
                    code_table = {(i,): i for i in range(1 << self._palette_bits)}

        stream.encode_bits(code_table[pattern], code_length)
        stream.encode_bits(self._end_code, code_length)
        return bytearray([self._palette_bits]) + stream.dump_bytes() + bytearray([0])
        
    def save_gif(self, filename):
        """Note the 'wb' mode here!"""
        with open(filename, 'wb') as f:
            f.write(self.logical_screen_descriptor +
                    self.global_color_table +
                    self.loop_control +
                    self.data +
                    self.trailor)


def example1():
    width = 400
    height = 200
    min_bits = 3
    palette = [255, 0, 0,
               255, 125, 0,
               255, 255, 0,
               0, 255, 0,
               0, 0, 255,
               0, 255, 255,
               255, 0, 255,
               0, 0, 0]
    loop = 0
    writer = GIFWriter(width, height, min_bits, palette, loop)
    descriptor = writer.image_descriptor(0, 0, width, height)
    graphics_control = writer.graphics_control_block(delay=200, trans_index=7)

    for i in range(7):
        framei = [i] * width * height
        writer.data += graphics_control + descriptor + writer.LZW_encode(framei)

    writer.save_gif("example.gif")

def example2():
    # A 1x1 tiny gif example.
    # For a static gif image the `graphics_control_block` is not needed.
    width, height = 1, 1
    min_bits = 1
    palette = [255, 0, 0,
               0, 0, 0]
    loop = 0
    writer = GIFWriter(width, height, min_bits, palette, loop)
    descriptor = writer.image_descriptor(0, 0, width, height)
    writer.data += descriptor + writer.LZW_encode([0])
    writer.save_gif("tiny1x1.gif")


if __name__ == "__main__":
    example1()
    example2()
