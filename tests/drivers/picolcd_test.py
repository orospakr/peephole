import unittest

import struct

from tests.util import packet_fixture
import peephole.drivers.picolcd

class PicoLCDTest(unittest.TestCase):

    PACKET_BACKLIGHT_ON = packet_fixture(
        [0x91, 0x01]
        )

    PACKET_BACKLIGHT_OFF = packet_fixture(
        [0x91, 0x00]
        )

    PACKET_FLASH_INTERNAL_EEPROM = packet_fixture(
        [0x32, 0x00]
        )

    def setUp(self):
        self.picolcd = peephole.drivers.picolcd.PicoLCD()



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
        self.assertEquals(on_packet, self.PACKET_BACKLIGHT_ON)

    def testGenerateBacklightTurnOff(self):
        off_packet = self.picolcd.generate_backlight_packet(False)
        self.assertEquals(off_packet, self.PACKET_BACKLIGHT_OFF)

    def writeInternalEepromTest(self):
        pass





