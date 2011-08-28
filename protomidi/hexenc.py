import sys


class HexEncoder:
    """
    Wraps around a filelike object and convert each byte to a three
    character sequence: two hex chars encoding the byte and a whitespace
    character to delimit it from the next byte.
    
    After writing 'wraplen' bytes, the encoder will output a newline
    instead of a space after the hex byte. (Todo: allow the user to
    force a newline?)

    Todo: if wraplen == None, wrapping will not happen.

    Todo: create a StringIO object if file==None? This would be convenient.

    Todo: the encode can also be used like this:

           hexenc = HexEncoder()
           for i in range(10):
               outfile.write(hexenc.encode(i))

       or even:

           enc = HexEncoder()
    
           for i in range(10):
               outfile.write(enc(i))
    """

    def __init__(self, file=file, wraplen=None):
        """
        Create a new HexEncoder and wrap it around the filelike object
        'file'.
        """

        self.file = file
        self.wraplen = wraplen


    def write(self, data):

        for byte in data:
            byte = ord(byte)
            byte = self.encode(byte)

            self.file.write(byte)

            if self.wraplen:
                self.file.write('\n')
                self.pos = 0
            else:
                self.file.write(' ')

    def encode(self, byte):
        """
        Encode one byte and return it. They byte
        must be an integer in the range [0...255].
        """
        assert isinstance(byte, int)
        assert 0 <= byte < 255

        return ('%02x' % byte)

    __call__ = encode  # Convenient shortcut

    def flush(self):
        """
        Flush the output file.
        """

        self.out.flush()


if __name__ == '__main__':
    enc = HexEncoder(sys.stdout)
    
    print(' '.join([enc(i) for i in range(10)]))
