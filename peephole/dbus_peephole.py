import gobject
from gettext import gettext as _
import dbus
import dbus.service
import dbus.mainloop.glib
import logging
import struct
import sys

from peephole.dbus_lcd import DBusLCD
from peephole.dbus_settings import *

class DBusPeephole(dbus.service.Object):
    '''Singleton object exposed over D-Bus that lists all of the
    LCDs.'''

    def __init__(self, lcds, bus_or_tube):
        dbus.service.Object.__init__(self, bus_or_tube, PEEPHOLE_PATH)
        self.bus_or_tube = bus_or_tube
        self.lcds = lcds

    @dbus.service.method(dbus_interface=PEEPHOLE_INTERFACE,
                         in_signature='', out_signature='as')
    def GetLCDs(self):
        paths = []
        for lcd in self.lcds:
            paths.append(lcd.getPath())
        return paths
