__all__ = ['lzw_encoder', 'PALETTE_BITS']


PALETTE_BITS = 2
CLEAR_CODE = 4
END_CODE = 5
MAX_CODES = 4096


class LZWEncoder(object):

    def __init__(self):
        self.bitstream = bytearray()
        self.num_bits = 0


    def encode_bits(self, num, size):
        string = bin(num)[2:].zfill(size)
        for digit in reversed(string):
            if len(self.bitstream) * 8 == self.num_bits:
                self.bitstream.append(0)
            if digit == '1':
                self.bitstream[-1] |= 1 << self.num_bits % 8
            self.num_bits += 1


    def dump_bytes(self):
        bytestream = str()
        while len(self.bitstream) > 255:
            bytestream += chr(255) + self.bitstream[:255]
            self.bitstream = self.bitstream[255:]
        if self.bitstream:
            bytestream += chr(len(self.bitstream)) + self.bitstream

        self.reset()
        return bytestream


    def __call__(self, imagedata, *color_indexes):
        code_length = PALETTE_BITS + 1
        next_code = END_CODE + 1
        code_table = {str(i): c for i, c in enumerate(color_indexes)}
        self.encode_bits(CLEAR_CODE, code_length)

        pattern = str()
        for c in map(str, imagedata):
            pattern += c
            if not code_table.has_key(pattern):
                code_table[pattern] = next_code
                self.encode_bits(code_table[pattern[:-1]], code_length)
                pattern = c

                next_code += 1
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
