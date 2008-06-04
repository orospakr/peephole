
class VUMeter(object):

    def __init__(self, picolcd):
        self.picolcd = picolcd

    def generateBar(self, num):
        '''Generate a bar with a given height in PicoLCD character format.

        num -- the number of rows that should be darkened, starting from the
               bottom.

        Should be factored out somewhere.'''
        bar = ''
        for row in range(0,8):
            # I subtract one because this the row addressing is zero-based
            if row <= (num - 1):
                bar += '\x00'
            else:
                bar += '\x1F'
        return bar

    def writeVUBars(self):
        '''Writes a sequence of VU meter bars to the PicoLCD CG RAM with
        addresses 1 through 7.  0 is left unused.

        Should be factored out somewhere.
        '''
        #self.upload_char(0, "\x1F\x1F\x1F\x1F\x1F\x1F\x1F")
        #self.upload_char(0, "936578f")
        # we skip the first char ID because we don't need it, and so can use it
        # for something else.
        for char_id in range(1,8):
            character = self.generateBar(char_id - 1)
            #character = "1234567"
            self.picolcd.upload_char(char_id, character)
