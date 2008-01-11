# Peephole - A D-Bus service for LCD displays
# Copyright (C) 2007, 2008 Infoglobe

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

USB_INTERRUPTREAD_TIMEOUT = 4000

def replace_text(orig_buffer, new_content, col):
    '''Replaces the contents of orig_buffer at col with new_content.'''
    return orig_buffer[:col] + new_content + orig_buffer[col+len(new_content):]

class PicoLCDButtonListener(threading.Thread):
    def __init__(self, lcd, button_cb):
        threading.Thread.__init__(self)
        self.lcd = lcd
        self.button_cb = button_cb
        self.please_stop = False

    def check_if_time_to_stop(self):
        return self.please_stop

    def run(self):
        '''This is what is run in the Thread when it is started.'''
        logging.debug(_("PicoLCD button listener thread now running."))
        while True:
            if self.please_stop:
                return
            button = self.lcd.get_button(self.check_if_time_to_stop)
            if self.button_cb is not None and button is not None:
                logging.debug("Button was: %s" % button)
                self.button_cb(button)

    def shutdown(self):
        '''Called by the main thread to stop the this button listener thread.'''
        self.please_stop = True

class PicoLCDHardware(object):
    '''Wraps the USB connectivity for the PicoLCD 20x2 device.'''

    # USB device IDs
    VENDOR_ID = 0x04d8
    DEVICE_ID = 0x0002

    def __init__(self):
        self.lcd_device = peephole.drivers.driver.get_usb_device(self.VENDOR_ID, self.DEVICE_ID)
        if self.lcd_device is None:
            sys.exit(_("PicoLCD not found."))
        self.lcd_handle = self.lcd_device.open()
        try:
            self.lcd_handle.detachKernelDriver(0)
        except usb.USBError, e:
            logging.warn(_("Could not detach kernel driver."))
        self.lcd_configuration = self.lcd_device.configurations[0]
        self.lcd_handle.setConfiguration(self.lcd_configuration)
        time.sleep(0.009) # for shame

        # we know it's the first interface's only option (there are
        # no alternate interfaces)
        self.lcd_interface = self.lcd_configuration.interfaces[0][0]
        #self.lcd_handle.detachKernelDriver(self.lcd_interface)
        interface = self.lcd_handle.claimInterface(self.lcd_interface)
        interface_alt = self.lcd_handle.setAltInterface(self.lcd_interface)

        self.lcd_interface = self.lcd_configuration.interfaces[0][0]
        time.sleep(1) # also for shame
        #self.start_button_listener()

    def write_command(self, packet):
        endp = self.lcd_interface.endpoints[1]
        self.lcd_handle.interruptWrite(endp.address, packet, 1000)

    def get_button(self, should_i_stop):
        '''Blocks until a button down event is detected, and returns it.'''
        endp = self.lcd_interface.endpoints[0]
        while True:
            logging.debug(_("Re-running interruptRead loop..."))
            if should_i_stop() is True:
                return None
            try:
                packet = self.lcd_handle.interruptRead(endp.address, 24, USB_INTERRUPTREAD_TIMEOUT)
            except usb.USBError: # it throws an exception if the timeout is hit.
                continue
            if packet[0] == 0x11:
                if packet[1] == 0:
                    continue
                logging.debug(_("Button pressed: x%02x" % packet[1]))
                return packet[1]

class PicoLCD(peephole.drivers.driver.Driver):
    '''Represents a picoLCD device.'''
    PICOLCD_CLEAR_CMD   = 0x94
    PICOLCD_DISPLAY_CMD = 0x98
    PICOLCD_SETFONT_CMD = 0x9C
    PICOLCD_REPORT_INT_EE_WRITE = 0x32

    # these two strings contain the contents of the display as we know it.
    # this is done because the device is write-only, and we need to know what
    # the contents are for the "burn in" feature.
    contents = ['' * 20, '' * 20]

    def generate_text_packet(self, text, row, col):
        assert(len(text) < 256)
        fmt = 'BBBB%is' % len(text)
        return struct.pack(fmt, self.PICOLCD_DISPLAY_CMD, row, col, len(text), text)

    def clear(self):
        packet = struct.pack('B', self.PICOLCD_CLEAR_CMD)
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
        packet = struct.pack('BB7sx', self.PICOLCD_SETFONT_CMD, char_id, character)
        self.lcd.write_command(packet)

    def generate_bar(self, num):
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

    def write_vu_bars(self):
        '''Writes a sequence of VU meter bars to the PicoLCD CG RAM with
        addresses 1 through 7.  0 is left unused.

        Should be factored out somewhere.
        '''
        #self.upload_char(0, "\x1F\x1F\x1F\x1F\x1F\x1F\x1F")
        self.upload_char(0, "936578f")
        # we skip the first char ID because we don't need it, and so can use it
        # for something else.
        for char_id in range(1,8):
            character = self.generate_bar(char_id - 1)
            #character = "1234567"
            self.upload_char(char_id, character)

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

    def __init__(self):
        pass

    def start(self):
        '''We have this logic started separately from the class constructor,
        so this class can be instantiated by the test suite.'''
        self.lcd = PicoLCDHardware()

    def set_text(self, text, row, col):
        # the +1s are because col is the column number, which is zero based.
        #new = self.contents[row][:col+1] + text + self.contents[row][:col+1+len(text)]
        new = replace_text(self.contents[row], text, row) 
        self.contents[row] = new[:20]
        try:
            assert len(self.contents[row]) == 20
        except AssertionError:
            logging.debug("the row was %i, which should never be different than 20!" % len(self.contents[row]))
        logging.debug('Row %i now contains "%s".' % (row, self.contents[row]))
        # we don't actually send the contents buffer.  The device is faster (I think)
        # if you just send the changed bit, so we might as well, because this code
        # is known good.
        packet = self.generate_text_packet(text, row, col)
        self.lcd.write_command(packet)

    def start_button_listener(self):
        logging.info(_("Starting button listener thread."))

        self.listener_thread = PicoLCDButtonListener(self.lcd, self.button_cb)
        self.listener_thread.start()
        time.sleep(3)
        logging.info(_("Thread started."))

    def get_lines(self):
        '''The PicoLCD 20x2 always has two lines -- who-da thunk it?'''
        len(self.contents)

    def generate_splash_packet(self, number, contents):
        pass

    def burn_screen(self):
        '''Makes the current contents of the display permanent, in that they
        will be automatically displayed when the device is powered up.  This
        uses the "splash screen" feature of the device.

        The PicoLCD device has a more comprehensive interface than this,
        but Peephole is meant to take a lowest common denominator approach.
        '''
        packet = self.generate_splash_packet(self.contents)
        self.lcd.write_command(packet)

    def stop(self):
        '''Stop the driver.'''
        logging.info("Attempting to stop PicoLCD button listener thread...")
        self.listener_thread.shutdown()
        logging.info("Request sent.  Please wait a moment...")
        self.listener_thread.join()
