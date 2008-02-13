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

    @virtual
    def scancode_to_keysym(self):
        '''Callback used to convert a hardware scancode into the
        Peephole keysym format (which is shameless ripped from
        the X11 keysym table.  If there's a keysym you wish to use,
        feel free to add it.'''

    @virtual
    def start(self):
        '''Called at boot when Peephole wishes to actually start
        the driver and device.'''

    @virtual
    def set_text(self, text, row, col):
        '''Set the string text at row and column of
        the display.'''

    @virtual
    def add_button_callback(self, cb):
        '''Adds a callback to be fired.

        The callback will be threadsafe (it will of course need
        the GIL).'''

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

        This we be called before start().

        self.button_cbs.append(cb)
        '''

    @virtual
    def fire_btn_cb(self, button):
        '''You should call this inside your driver whenever you have new
        button presses available.

        (You can also manually iterate over button_cbs if you really want to...'''

        for cb in self.button_cbs:
            cb(button)





