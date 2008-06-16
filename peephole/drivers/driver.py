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
from gettext import gettext as _
import logging
from peephole.util import virtual

def replace_text(orig_buffer, new_content, col, rowlen):
    '''Replaces the contents of orig_buffer at col with new_content.'''
    if (len(new_content) + col) > rowlen:
        raise ValueError, _("Too big to fit on the display!")
    return orig_buffer[:col] + new_content + orig_buffer[col+len(new_content):]

def get_usb_device(vendor_id, device_id):
    buses = usb.busses()
    for bus in buses:
        for device in bus.devices:
            if device.idVendor == vendor_id and device.idProduct == device_id:
                return device
    return None

class Driver(object):
    '''Defines the interface that needs to be implemented by
    Peephole device drivers.

    When adding a driver to Peephole, you must implement the
    interface defined here.  These methods are called by Peephole's
    core to actually do the work.  Some of the below methods (the
    ones that aren't decorated @virtual) are convenience methods.
    You don't need or want to overload those.

    You are allowed to spawn a thread to do jobs like listening
    for key events (see the PicoLCD driver for an example thereof).

    TODO -- make non-essential non-implemented methods throw a nicer
    exception for D-Bus clients so they know that particular device
    does not support that feature.
    '''
    def __init__(self):
        self.button_cbs = []
        self.button_created_cbs = []
        self.buttons = []

#     @virtual
#     def scancode_to_keysym(self):
#         '''Callback used to convert a hardware scancode into the
#         Peephole keysym format (which is shameless ripped from
#         the X11 keysym table.  If there's a keysym you wish to use,
#         feel free to add it.'''

    @virtual
    def start(self):
        '''Called at boot when Peephole wishes to actually start
        the driver and device.'''

    @virtual
    def set_text(self, text, row, col):
        '''Set the string text at row and column of
        the display.'''

    @virtual
    def get_lines(self):
        '''Returns the number of lines available on the display.

        This will probably be deprecated in favour of a more
        comprehensive get_geometry() method.
        '''

    @virtual
    def set_backlight(self, status):
        '''Turns the device's backlight on or off.'''

    @virtual
    def draw_meter(self, value):
        '''Draws a simple VU meter on the display of the LCD.  You can
        implement this with whatever method is best suited for the device.

        Intended mostly as a convenience "I need it to work now" function.'''

    @virtual
    def get_name(self):
        '''Returns the name of this instance of the device.  This is used in the
        D-Bus path, so please don't use any spaces or otherwise weird
        characters.  Remember, this should return something different
        for different instances of this device, in case there is more than
        one plugged in.'''

    def add_button_callback(self, cb):
        '''This is called by Peephole's core, to register a callback function
        that your driver should call whenever a new button event is available.

        This will be called before start().

        '''
        self.button_cbs.append(cb)

    def addButton(self, button):
        self.buttons.append(button)
        self.new_button_added(button)

    def add_button_created_callback(self, cb):
        self.button_created_cbs.append(cb)

    def fire_btn_cb(self, button_keysym):
        '''You should call this inside your driver whenever you have new
        button presses available.
b
        The button callbacks expect one argument, in the form of an Peephole
        keysym, which is more or less the same as the X11 keysyms.  So, in your
        driver, use the appropriate value in peephole.drivers.buttons and call
        this method when you have a key press ready.

        (You can also manually iterate over button_cbs if you really want to...)'''
        for cb in self.button_cbs:
            cb(button_keysym)

    def new_button_added(self, button):
        for cb in self.button_created_cbs:
            cb(button)

    def pressButtonByName(self, name):
        for button in self.buttons:
            if button.name == name:
                button.pressed()

