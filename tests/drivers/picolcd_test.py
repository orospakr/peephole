import unittest

import struct
import pmock

from tests.util import packet_fixture
import peephole.drivers.picolcd
from peephole.drivers import buttons

class PicoLCDHardware(pmock.MockTestCase):
    def setUp(self):
        self.picolcd_usb = self.mock()
        self.picolcd_handle = self.mock()
        self.picolcd_configuration = self.mock()
        self.picolcd_usb.expects(pmock.once()).open().will(pmock.return_value(self.picolcd_handle))
        self.picolcd_configuration = self.mock()
        self.picolcd_interface = self.mock()
        self.picolcd_configuration.interfaces = [ [ self.picolcd_interface ] ]
        self.picolcd_usb.configurations = [self.picolcd_configuration]
        self.picolcd_handle.expects(pmock.once()).detachKernelDriver(pmock.eq(0))
        self.picolcd_handle.expects(pmock.once()).setConfiguration(pmock.same(self.picolcd_configuration))
        self.picolcd_handle.expects(pmock.once()).claimInterface(pmock.same(self.picolcd_interface))
        self.picolcd_handle.expects(pmock.once()).setAltInterface(pmock.same(self.picolcd_interface))
        self.hw = peephole.drivers.picolcd.PicoLCDHardware(self.picolcd_usb)

    def testInstantiate(self):
        self.failIfEqual(None, self.hw)

    def sendEvent(self, packet):
        endpoint = self.mock()
        endpoint.address = 2
        self.one_run_completed = False
        self.picolcd_interface.endpoints = [endpoint]
        def should_i_stop():
            if self.one_run_completed:
                return True
            else:
                self.one_run_completed = True
                return False
        self.picolcd_handle.expects(pmock.once()).interruptRead(pmock.eq(2), pmock.eq(24), pmock.eq(4000)).will(pmock.return_value(packet))
        return self.hw.get_event(should_i_stop)


    def testReceiveButtonEvent(self):
        packet = [0x11, 0x04, 0x00]
        button_result = self.sendEvent(packet)
        self.failUnlessEqual(button_result, buttons.XK_F2)

    def testReceiveSpuriousEmptyEvent(self):
        # check that we gracefully handle this weird case that
        # was causing Peephole to crash randomly after a while
        # of use.
        packet = []
        button_result = self.sendEvent(packet)
        self.failUnlessEqual(None, button_result)

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
        self.picolcd = peephole.drivers.picolcd.PicoLCD(None)

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





