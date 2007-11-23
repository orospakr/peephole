#!/usr/bin/env python

import gobject
from gettext import gettext as _
import dbus
import dbus.service
import dbus.mainloop.glib
import struct
import sys
import time
import usb

#  dbus-send --print-reply --type=method_call --system --dest='org.orospakr.peephole' /org/orospakr/peephole/LCDs/PicoLCD org.orospakr.peephole.LCD.DisplayText string:0 string:"stuffs"

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


class PicoLCD(object):
    '''Represents a picoLCD device.'''

    # USB device IDs
    VENDOR_ID = 0x04d8
    DEVICE_ID = 0x0002

    PICOLCD_DISPLAY_CMD = 0x98

    def __init__(self):
        self.lcd_device = get_usb_device(self.VENDOR_ID, self.DEVICE_ID)
        if self.lcd_device is None:
            sys.exit(_("No such device."))
        self.lcd_handle = self.lcd_device.open()
        self.lcd_handle.detachKernelDriver(0)
        self.lcd_configuration = self.lcd_device.configurations[0]
        print("%s" % self.lcd_device.configurations[0])
        self.lcd_handle.setConfiguration(self.lcd_configuration)
        time.sleep(0.001) # for shame

        # we know it's the first interface's only option (there are
        # no alternate interfaces)
        self.lcd_interface = self.lcd_configuration.interfaces[0][0]
        #self.lcd_handle.detachKernelDriver(self.lcd_interface)
        interface = self.lcd_handle.claimInterface(self.lcd_interface)
        interface_alt = self.lcd_handle.setAltInterface(self.lcd_interface)

        self.lcd_interface = self.lcd_configuration.interfaces[0][0]

    def set_text(self, text, row, col):
        assert(len(text) < 256)

        endp = self.lcd_interface.endpoints[1]
        fmt = 'BBBB%is' % len(text)
        print len(text)
        packet = struct.pack(fmt, self.PICOLCD_DISPLAY_CMD, row, col, len(text), text)
        self.lcd_handle.interruptWrite(endp.address, packet, 1000)

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

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='is', out_signature='')
    def DisplayText(self, line_number, text):
        print _("User asked to display: %s") % text
        self.lcd.set_text(str(text), 0, 0)

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='', out_signature='i')
    def GetLines(self):
        return 2

mainloop = gobject.MainLoop()
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

system_bus = dbus.SystemBus()
name = dbus.service.BusName(PEEPHOLE_WELL_KNOWN_NAME, system_bus)
my_lcd = PicoLCD()
object = DBusLCD(my_lcd, system_bus, 'PicoLCD')

mainloop.run()
