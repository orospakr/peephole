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
