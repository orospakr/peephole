import unittest

import peephole.drivers.picolcd

class PicoLCDTest(unittest.TestCase):

    def setUp(self):
        self.picolcd = peephole.drivers.picolcd.PicoLCD()

    def testReplaceText(self):
        row =          "  Hello Computer    "
        replace_text = "  Bye"
        replace_at = 2 # zero-based
        final_text   = "    Bye Computer    "
        self.assertEqual(len(row), 20)

        result = peephole.drivers.picolcd.replace_text(row, replace_text, replace_at)
        
        #self.assertEqual(len(result), 20)

        self.assertEqual(final_text, result)

    def testGenerateText(self):
        '''Maybe this should use a fixture packet rather than just generating
        one with a copy pasta'd copy of the algorithm. :P'''
        import struct

        message = "my message!"
        fmt = 'BBBB%is' % len(message)
        correct_contents = struct.pack(fmt,
                                       peephole.drivers.picolcd.PicoLCD.PICOLCD_DISPLAY_CMD,
                                       0, 0, len(message), message)

        packet = self.picolcd.generate_text_packet(message, 0, 0)
        self.assertEquals(packet, correct_contents)
