#!/usr/bin/env python

# Peephole - an LCD D-Bus Service daemon.
# Copyright (C) 2007 Infoglobe

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

import gobject
from gettext import gettext as _
import dbus
import dbus.service
import dbus.mainloop.glib
import logging
import struct
import sys
#import time
#import threading
#import usb

#  dbus-send --print-reply --type=method_call --system --dest='org.orospakr.peephole' /org/orospakr/peephole/LCDs/PicoLCD org.orospakr.peephole.LCD.DisplayText string:0 string:"stuffs"

import peephole.drivers.picolcd

LCD_INTERFACE = 'org.orospakr.peephole.LCD'
PEEPHOLE_WELL_KNOWN_NAME = 'org.orospakr.peephole'
LCD_PATH_BASE = '/org/orospakr/peephole/LCDs/'

def get_usb_device(vendor_id, device_id):
    buses = usb.busses()
    for bus in buses:
        for device in bus.devices:
            if device.idVendor == vendor_id and device.idProduct == device_id:
                return device
    return None



class DBusLCD(dbus.service.Object):
    '''Object exposing an LCD over D-Bus.

    lcd -- LCD object representing the actual hardware.

    bus_or_tube -- D-Bus bus or Telepathy Tube to publish this LCD over.

    device_name -- Friendly name for the device, for D-Bus path.
    '''

    def __init__(self, lcd, bus_or_tube, device_name):
        dbus.service.Object.__init__(self, bus_or_tube, LCD_PATH_BASE + device_name)
        self.path = device_name
        self.bus_or_tube = bus_or_tube
        self.lcd = lcd
        lcd.button_cb = self.ButtonPressed
        lcd.start_button_listener()

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='is', out_signature='')
    def DisplayText(self, line_number, text):
        logging.debug(_("User asked to display: %s") % text)
        self.lcd.set_text(str(text), int(line_number), 0)

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='', out_signature='i')
    def GetLines(self):
        self.lcd.get_lines()

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='d', out_signature='')
    def DrawVUMeter(self, value):
        self.lcd.draw_meter(value)

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='', out_signature='')
    def Clear(self):
        self.lcd.clear()

    @dbus.service.signal(dbus_interface=LCD_INTERFACE,
                         signature='i')
    def ButtonPressed(self, button):
        pass

if __name__ == "__main__":
    print("Peephole.")

    logging.basicConfig(level=logging.DEBUG)

    gobject.threads_init()

    mainloop = gobject.MainLoop()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    system_bus = dbus.SystemBus()
    name = dbus.service.BusName(PEEPHOLE_WELL_KNOWN_NAME, system_bus)
    my_lcd = peephole.drivers.picolcd.PicoLCD()
    my_lcd.start()
    my_lcd.clear()
    my_lcd.write_vu_bars()
    my_lcd.set_text("\x06\x05\x04\x03\x02\x01Peephole\x01\x02\x03\x04\x05\x06", 0, 0)
    #my_lcd.draw_meter(0)
    #my_lcd.test_spin()
    #sys.exit()
    # while True:
    #     my_lcd.get_button()
    object = DBusLCD(my_lcd, system_bus, 'PicoLCD')

    try:
        mainloop.run()
    except KeyboardInterrupt:
        # program is now quitting, so...
        my_lcd.stop()
