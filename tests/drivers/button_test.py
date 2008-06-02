import unittest

import struct
from pmock import *

from tests.util import packet_fixture
import peephole.drivers.picolcd
from peephole.drivers import buttons

from peephole.drivers.button import Button

class ButtonTest(MockTestCase):
    def setUp(self):
        self.lcd = self.mock()
        self.button = Button(self.lcd, 'F1', buttons.XK_F1)

    def testInstantiation(self):
        pass

    def testShouldCallLCDButtonSetBacklightWhenSetBacklightCalled(self):
        self.lcd.expects(once()).setButtonBacklight(same(self.button), eq(True))
        self.button.setBacklight(True)

    def testShouldCallRegisteredCallbackWhenPressed(self):
        self.pressed = False
        def pressed_callback():
            self.pressed = True
        self.button.registerPressedCallback(pressed_callback)
        self.lcd.expects(once()).fire_btn_cb(eq(buttons.XK_F1))
        self.button.pressed()
        self.failUnlessEqual(True, self.pressed)
