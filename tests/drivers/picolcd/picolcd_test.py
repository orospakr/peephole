import unittest

import struct
import pmock
from pmock import *
import gobject

from tests.util import packet_fixture
from tests import *
from peephole.drivers.picolcd.picolcd import PicoLCD
from peephole.drivers import buttons

from peephole.drivers.picolcd.consts import *

class PicoLCDTest(MockTestCase):

    PACKET_BACKLIGHT_ON = packet_fixture(
        [0x91, 0x01]
        )

    PACKET_BACKLIGHT_OFF = packet_fixture(
        [0x91, 0x00]
        )

    PACKET_FLASH_INTERNAL_EEPROM = packet_fixture(
        [0x32, 0x00]
        )

    PACKET_SET_LED_TURN_LED_2_ON = packet_fixture(
        [0x81, 0x20]
        )

    PACKET_SET_LED_TURN_LED_7_ON = packet_fixture(
        [0x81, 0x01]
        )

    def setUp(self):
        self.factory = self.mock()
        self.event_listener = self.mock()
        self.usb_device = self.mock()
        self.buttons = []



        self.picolcd = PicoLCD(self.usb_device,
                               factory_mock=self.factory)

        # buttons!

        for (name, keysym) in PicoLCD.button_map.items():
            new_button = self.mock()
            new_button.name = name
            new_button.keysym = keysym
            self.buttons.append(new_button)
            #self.factory.expects(once()).makeButton(same(self.picolcd), eq(name), eq(keysym))

        self.factory.expects(once()).makeButtons(same(self.picolcd), eq(PicoLCD.button_map)).will(return_value(self.buttons))


        self.device = self.mock()
        self.event_listener = self.mock()
        self.vu_meter = self.mock()

        self.device.expects(once()).start()
        self.factory.expects(once()).makeDevice(same(self.usb_device)).will(return_value(self.device))
        self.factory.expects(once()).makeEventListener(same(self.device)).will(return_value(self.event_listener))
        self.factory.expects(once()).makeVUMeter(same(self.picolcd)).will(return_value(self.vu_meter))

        self.vu_meter.expects(once()).writeVUBars()

        self.event_listener.expects(once()).connect(eq('buttonPressed'), bound_method(PicoLCD, 'onButtonPressed'))
        self.event_listener.expects(once()).start()

        self.picolcd.start()

    def testStart(self):
        pass

    def getButtonMockByKeysym(self, keysym):
         for button in self.buttons:
            if button.keysym == keysym:
                return button

    def testFindButtonByKeysym(self):
        b = self.getButtonMockByKeysym(buttons.XK_F3)

        result = self.picolcd.findButtonByKeysym(buttons.XK_F3)
        self.failUnlessEqual('F3', result.name)

    def testGenerateText(self):
        '''Maybe this should use a fixture packet rather than just generating
        one with a copy pasta'd copy of the algorithm. :P'''

        message = "my message!"
        fmt = 'BBBB%is' % len(message)
        correct_contents = struct.pack(fmt,
                                       PICOLCD_DISPLAY_CMD,
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

    def testButtonPressed(self):
        self.legacy_button_keysym = None

        def legacy_button_callback(btn):
            self.legacy_button_keysym = btn

        self.picolcd.add_button_callback(legacy_button_callback)
        f5_button_mock = self.getButtonMockByKeysym(buttons.XK_F5)
        f5_button_mock.expects(once()).pressed()

        self.picolcd.onButtonPressed(0x07)

        self.failUnlessEqual(self.legacy_button_keysym, buttons.XK_F5)

    def testGenerateLedPacket(self):
        self.picolcd.leds = [0, 1, 0, 0, 0, 0, 0]
        led2on_packet = self.picolcd.generate_setled_packet()
        self.assertEquals(led2on_packet, self.PACKET_SET_LED_TURN_LED_2_ON)


    def testGenerateLedPacketEdge(self):
        self.picolcd.leds = [0, 0, 0, 0, 0, 0, 1]
        led2on_packet = self.picolcd.generate_setled_packet()
        self.assertEquals(led2on_packet, self.PACKET_SET_LED_TURN_LED_7_ON)
