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

import time
import usb
import logging
from gettext import gettext as _
from peephole.drivers.picolcd.consts import *

class Device(object):
    '''Wraps the USB connectivity for the PicoLCD 20x2 device.'''

    def __init__(self, lcd_device):
        self.lcd_device = lcd_device
        if self.lcd_device is None:
            raise ValueError, _("PicoLCD not found.")
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

    def start(self):
        pass

    def write_command(self, packet):
        endp = self.lcd_interface.endpoints[1]
        self.lcd_handle.interruptWrite(endp.address, packet, 1000)

    def get_event_nonblock(self):
        endp = self.lcd_interface.endpoints[0]
        packet = self.lcd_handle.interruptRead(endp.address, 24, FAST_USB_INTERRUPTREAD_TIMEOUT)
        if packet[0] == PICOLCD_GET_KEYDATA:
            if packet[1] != 0:
                return packet[1]
        return None

    def get_event(self, should_i_stop):
        '''Blocks until a PicoLCD event is detected, and returns it.'''
        endp = self.lcd_interface.endpoints[0]
        while True:
            logging.debug(_("Re-running interruptRead loop..."))
            if should_i_stop() is True:
                return None
            try:
                packet = self.lcd_handle.interruptRead(endp.address, 24, USB_INTERRUPTREAD_TIMEOUT)
            except usb.USBError: # it throws an exception if the timeout is hit.
                continue
            if len(packet) == 0:
                logging.info(_('Received spurious empty packet.'))
                continue
            # just for testing the infrared detector
            if packet[0] == PICOLCD_GET_IRDATA:
                print packet

            if packet[0] == PICOLCD_GET_KEYDATA:
                if packet[1] == 0:
                    continue
                logging.debug(_("Button pressed: x%02x" % packet[1]))
                return packet[1]
