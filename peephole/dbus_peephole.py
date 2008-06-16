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
