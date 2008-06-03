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
        self.backlight_cb_called = False
        def backlight_cb(state):
            self.failUnlessEqual(True, state)
            self.backlight_cb_called = True
        self.button.registerBacklightCallback(backlight_cb)
        self.button.setBacklight(True)
        self.failUnlessEqual(True, self.backlight_cb_called)

    def testShouldCallRegisteredCallbackWhenPressed(self):
        self.pressed = False
        def pressed_callback():
            self.pressed = True
        self.button.registerPressedCallback(pressed_callback)
        self.lcd.expects(once()).fire_btn_cb(eq(buttons.XK_F1))
        self.button.pressed()
        self.failUnlessEqual(True, self.pressed)
