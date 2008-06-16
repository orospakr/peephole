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

from peephole.dbus_settings import *

class DBusButton(dbus.service.Object):
    '''Object exposing a button beloging to an LCD over D-Bus.'''

    def __init__(self, dbus_lcd, button):
        self.dbus_lcd = dbus_lcd
        self.button = button
        dbus.service.Object.__init__(self, dbus_lcd.bus_or_tube, self.getPath())
        self.button.registerPressedCallback(self.Pressed)

    def getPath(self):
        return self.dbus_lcd.getPath() + '/Buttons/' + self.button.name

    @dbus.service.signal(dbus_interface=BUTTON_INTERFACE,
                         signature='')
    def Pressed(self):
        pass

    @dbus.service.method(dbus_interface=BUTTON_INTERFACE,
                         in_signature='b', out_signature='')
    def SetBacklight(self, state):
        self.button.setBacklight(state)

    @dbus.service.method(dbus_interface=BUTTON_INTERFACE,
                         in_signature='', out_signature='s')
    def GetName(self):
        return self.button.name

    @dbus.service.method(dbus_interface=BUTTON_INTERFACE,
                         in_signature='', out_signature='i')
    def GetX11Keysym(self):
        return self.button.keysym
