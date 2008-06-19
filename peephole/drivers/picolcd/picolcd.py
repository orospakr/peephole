# Peephole - a D-Bus service providing access to small LCD panels
# Copyright (C) 2007-2008 Andrew Clunis

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import usb
import threading
import logging
import struct
import sys
import time
from gettext import gettext as _

import peephole.drivers.driver
from peephole.drivers import buttons
from peephole.drivers.picolcd.factory import Factory

from peephole.drivers.picolcd.consts import *

class PicoLCD(peephole.drivers.driver.Driver):
    '''Represents a picoLCD device.'''

    button_map = { 'F1': (buttons.XK_F1, 5), 'F2': (buttons.XK_F2, 4),
                   'F3': (buttons.XK_F3, 3), 'F4': (buttons.XK_F4, 2),
                   'F5': (buttons.XK_F5, 1),
                   'Up': (buttons.XK_Up, 6), 'Down' : (buttons.XK_Down, 6),
                   'OK': (buttons.XK_Return, 6),
                   'Left': (buttons.XK_Left, 6), 'Right': (buttons.XK_Right, 6),
                   'Plus': (buttons.XK_plus, 0), 'Minus': (buttons.XK_minus, 0)}


    def __init__(self, usb_device, factory_mock=None):
        # these two strings contain the contents of the display as we know it.
        # this is done because the device is write-only, and we need to know what
        # the contents are for the "burn in" feature
        self.contents = [' ' * 20, ' ' * 20]
        self.leds = [0, 0, 0, 0, 0, 0, 0]
        peephole.drivers.driver.Driver.__init__(self)
        self.usb_device = usb_device
        if factory_mock is not None:
            self.factory = factory_mock
        else:
            self.factory = Factory()

    def generate_text_packet(self, text, row, col):
        assert(len(text) < 256)
        fmt = 'BBBB%is' % len(text)
        return struct.pack(fmt, PICOLCD_DISPLAY_CMD, row, col, len(text), text)

    def clear(self):
        packet = struct.pack('B', PICOLCD_CLEAR_CMD)
        self.lcd.write_command(packet)

    def upload_char(self, char_id, character):
        '''Writes a 5x7 character into the CG RAM (Character Generation
        RAM) of the PicoLCD device.

        char_id -- the index (from 0 to 7) of the special character.

        character -- string (7 bytes long), containing the character.  Each
                     byte represents a single row of the character, with
                     each bit corresponding to a single pixel.
        '''
        # the pad byte is important.
        assert char_id <= 7
        packet = struct.pack('BB7sx', PICOLCD_SETFONT_CMD, char_id, character)
        self.lcd.write_command(packet)

    def get_bar_addr_from_value(self, value):
        '''Returns the address of the appropriate VU meter bar character
        in the PicoLCD device memory, as set by write_vu_bars().'''
        if value == 0:
            return 31 # space character
        return 9 - (value + 1)

    def test_spin(self):
        while True:
            for i in range(1,9):
                #self.write_vu_bars()
                time.sleep(0.050)
                if i == 8:
                    self.set_text(' ', 0, 1)
                else:
                    self.set_text(chr(i), 0, 1)

    def draw_meter(self, value):
        '''Draws a little meter on the right hand side of the display.

        value -- a decimal number between 0 and 1.'''
        # probably not the best rounding job, but whatever.
        assert (value >= 0) and (value <= 1)
        rows = int(value * 14)
        assert value < 14

        if rows > 7:
            top_half_character = chr(self.get_bar_addr_from_value(rows-7))
            bottom_half_character = chr(self.get_bar_addr_from_value(7))
        else:
            top_half_character = ' '
            bottom_half_character = chr(self.get_bar_addr_from_value(rows))

        self.set_text(top_half_character, 0, 19)
        self.set_text(bottom_half_character, 1, 19)

    def start(self):
        '''We have this logic started separately from the class constructor,
        so this class can be instantiated by the test suite.'''
        self.lcd = self.factory.makeDevice(self.usb_device)
        self.lcd.start()
        self.start_button_listener()

        self.vu_meter = self.factory.makeVUMeter(self)
        self.vu_meter.writeVUBars()

        self.updateLeds()

        # buttons!
#        self.f1_button = self.factory.makeButton(self, 'F1', buttons.XK_F1)
        self.buttons = self.factory.makeButtons(self, self.button_map)

        for b in self.buttons:
            self.new_button_added(b)

    def findButtonByKeysym(self, keysym):
        for b in self.buttons:
            if b.keysym == keysym:
                return b

    def set_text(self, text, row, col):
        # the +1s are because col is the column number, which is zero based.
        #new = self.contents[row][:col+1] + text + self.contents[row][:col+1+len(text)]
        new = peephole.drivers.driver.replace_text(self.contents[row], text, col, 20)
        self.contents[row] = new[:20]
        try:
            assert len(self.contents[row]) == 20
        except AssertionError:
            logging.debug("the row length was %i, which should never be different than 20!" % len(self.contents[row]))
        #logging.debug('Row %i now contains "%s".' % (row, self.contents[row]))
        # we don't actually send the contents buffer.  The device is faster (I think)
        # if you just send the changed bit, so we might as well, because this code
        # is known good.
        packet = self.generate_text_packet(text, row, col)
        self.lcd.write_command(packet)

    def generate_backlight_packet(self, status):
        '''Returns a generated packet string to set the PicoLCD backlight
        to on or off, according to the boolean value status.'''
        fmt = 'BB'
        if status == True:
            packet = struct.pack(fmt, PICOLCD_BACKLIGHT, 1)
        else:
            packet = struct.pack(fmt, PICOLCD_BACKLIGHT, 0)
        return packet

    def set_backlight(self, status):
        logging.debug("Set backlight called with %s." % status)
        packet = self.generate_backlight_packet(status)
        self.lcd.write_command(packet)

    def onButtonPressed(self, listener, button):
        # legacy ButtonPressed event handlers...
        keysym = PICOLCD_KEYMAP[button]
#        for cb in self.button_cbs:
#            cb(keysym)
        self.findButtonByKeysym(keysym).pressed()

    def start_button_listener(self):
        logging.info(_("Starting button listener thread."))

#        self.listener_thread = PicoLCDButtonListener(self.lcd, self.button_cbs)
        self.event_listener = self.factory.makeEventListener(self.lcd)
        self.event_listener.connect('buttonPressed', self.onButtonPressed)
        self.event_listener.start()
        #time.sleep(3)
        logging.info(_("Thread started."))

    def get_lines(self):
        '''The PicoLCD 20x2 always has two lines -- who-da thunk it?'''
        len(self.contents)

    def generate_splash_packet(self, number, contents):
        fmt = 'BBBB40s'
        faddr = 0
        # I'm not sure what the constant 0x14 is meant to do.
        test_line = "     this is a test "
        test_line2= "   lol internet     "
        packet = struct.pack(fmt, PICOLCD_REPORT_INT_EE_WRITE,
                             faddr & 0xFF, (faddr >> 8) & 0xF, 0x14,
                             test_line + test_line2)
        return packet

    def burn_screen(self):
        '''Makes the current contents of the display permanent, in that they
        will be automatically displayed when the device is powered up.  This
        uses the "splash screen" feature of the device.

        The PicoLCD device has a more comprehensive interface than this,
        but Peephole is meant to take a lowest common denominator approach.
        '''
        packet = self.generate_splash_packet(0, self.contents)
        self.lcd.write_command(packet)

    def stop(self):
        '''Stop the driver.'''
        logging.info("Attempting to stop PicoLCD button listener thread...")
        self.event_listener.shutdown()
        logging.info("Request sent.  Please wait a moment...")
        self.event_listener.join()

    def updateLeds(self):
        self.lcd.write_command(self.generate_setled_packet())

    def set_leds(self, leds):
        self.leds = leds
        self.updateLeds()

    def generate_setled_packet(self):
        fmt = 'BB'
        led_byte = 0
        for i in range(0, 7):
            if self.leds[i] == 1:
                led_byte += (2 ** (8 - i - 2))
        print led_byte
        packet = struct.pack(fmt, PICOLCD_SET_LED_STATE, led_byte)
        return packet

    def get_name(self):
        return 'PicoLCD'

    def generate_eeprom_flash_packet(self, addr_hi, addr_lo, data):
        fmt = 'BBBB%is' % len(data)
        packet = struct.pack(fmt, PICOLCD_REPORT_INT_EE_WRITE, addr_hi, addr_lo, len(data), data)
        return packet

    def generate_splash_packet(self, line1, line2):
        header_fmt = 'BBBBB'
        leds = 0 # turn none of them on, for now.
        minutes = 0
        seconds = 5
        wtf = 0
        jump = 0
        repeat = 0
        header = struct.pack(header_fmt, seconds, wtf, jump, repeat, leds)
        big_packet = header + line1 + line2

        return self.generate_eeprom_flash_packet(0, 0, big_packet)
        # split 'im up!

