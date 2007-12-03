import unittest
import pmock

import peephole

class PicoLCDTest(unittest.TestCase):
    def setUp(self):
        self.picolcd = peephole.PicoLCD()

    def testGenerateText(self):
        '''Maybe this should use a fixture packet rather than just generating
        one with a copy pasta'd copy of the algorithm. :P'''
        import struct

        message = "my message!"
        fmt = 'BBBB%is' % len(message)
        correct_contents = struct.pack(fmt, peephole.PicoLCD.PICOLCD_DISPLAY_CMD, 0, 0, len(message), message)

        packet = self.picolcd.generate_text_packet(message, 0, 0)
        self.assertEquals(packet, correct_contents)


