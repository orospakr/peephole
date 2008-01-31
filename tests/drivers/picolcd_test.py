import unittest
from array import array
import struct

import peephole.drivers.picolcd

class PicoLCDTest(unittest.TestCase):

    # fixtures
    packet_backlight_on  = array('B', [0x91, 0x01]).tostring()
    packet_backlight_off = array('B', [0x91, 0x00]).tostring()

    def setUp(self):
        self.picolcd = peephole.drivers.picolcd.PicoLCD()

    def testReplaceText(self):
        row =          "  Hello Computer    "
        replace_text = "  Bye"
        replace_at = 2 # zero-based
        final_text   = "    Bye Computer    "
        self.assertEqual(len(row), 20)

        result = peephole.drivers.picolcd.replace_text(row, replace_text, replace_at)

        self.assertEqual(len(result), 20)

        self.assertEqual(final_text, result)

    def testGenerateText(self):
        '''Maybe this should use a fixture packet rather than just generating
        one with a copy pasta'd copy of the algorithm. :P'''

        message = "my message!"
        fmt = 'BBBB%is' % len(message)
        correct_contents = struct.pack(fmt,
                                       peephole.drivers.picolcd.PICOLCD_DISPLAY_CMD,
                                       0, 0, len(message), message)

        packet = self.picolcd.generate_text_packet(message, 0, 0)
        #print packet.__type__
        self.assertEquals(packet, correct_contents)

    def testGenerateBacklightTurnOn(self):
        on_packet = self.picolcd.generate_backlight_packet(True)
        self.assertEquals(on_packet, self.packet_backlight_on)

    def testGenerateBacklightTurnOff(self):
        off_packet = self.picolcd.generate_backlight_packet(False)
        self.assertEquals(off_packet, self.packet_backlight_off)



