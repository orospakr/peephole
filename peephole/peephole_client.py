#!/usr/bin/env python

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
from dbus.exceptions import DBusException
import logging
import struct
import sys
import os
from optparse import OptionParser

from peephole.peepholed import PEEPHOLE_WELL_KNOWN_NAME
from peephole.dbus_settings import *

def getButtons(selected_lcd, bus):
    button_paths = []
    buttons = {}
    button_paths = selected_lcd.GetButtons()
    for path in button_paths:
        button_proxy = bus.get_object(PEEPHOLE_WELL_KNOWN_NAME, path)
        button = dbus.Interface(button_proxy, dbus_interface=BUTTON_INTERFACE)
        button_name = button.GetName()
        buttons[button_name] = button
    return buttons

def main():
    usage = "%prog: [--lcd=LCD], needs one of [--list] [--print-buttons]"
    parser = OptionParser(usage)
    parser.add_option("-L", "--lcd", dest="lcd",
                      help="LCD to interact with")
    parser.add_option("-l", "--list", action="store_true",
                      dest="list",
                      help="Print list of LCDs in the system")
    parser.add_option("-b", "--print-buttons", action="store_true",
                      dest="print_buttons",
                      help="Print button events on stdout as they occur")
    parser.add_option("-B", "--button", dest="button",
                      help="Button to interact with, used with --set-button-backlight")
    parser.add_option("-O", "--button-backlight-on", dest="button_backlight", action="store_true",
                      help="Turn on button's (specified by --button) backlight")
    parser.add_option("-o", "--button-backlight-off", dest="button_backlight", action="store_false",
                      help="Turn off button's (specified by --button) backlight")


    (options, args) = parser.parse_args()

    if not (options.list or options.print_buttons or (options.button_backlight is not None)):
        parser.error("You must specify an option.")

    mainloop = gobject.MainLoop()

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    peep_proxy = bus.get_object(PEEPHOLE_WELL_KNOWN_NAME,
                                PEEPHOLE_PATH)

    peep = dbus.Interface(peep_proxy, dbus_interface=PEEPHOLE_INTERFACE)

    try:
        lcd_paths = peep.GetLCDs()
    except DBusException, e:
        print "\nPeephole D-Bus service is unavailable.  Possible causes: \n\
1. Missing D-Bus activation configuration -- alternatively, the daemon may \n\
   also be invoked manually. \n\
2. Missing security policy (see README) \n\
3. Daemon was started, but no LCDs were detected."
        sys.exit(-1)
    lcds = {}

    for path in lcd_paths:
        lcd_proxy = bus.get_object(PEEPHOLE_WELL_KNOWN_NAME, path)
        lcd = dbus.Interface(lcd_proxy, dbus_interface=LCD_INTERFACE)
        lcd_name = lcd.GetName()
        lcds[lcd_name] = lcd

    if options.list:
        for name, lcd in lcds.items():
            print name
        sys.exit(0)

    selected_lcd = None
    if options.lcd is not None:
        if options.lcd not in lcds:
            parser.error("That LCD does not exist.")
        selected_lcd = lcds[options.lcd]
        print "Selected: '%s'" % options.lcd
    else:
        for name, l in lcds.items():
            print "Fell back to default LCD: '%s'" % name
            selected_lcd = l
            break
    buttons = getButtons(selected_lcd, bus)

    if options.button_backlight is not None:
        if options.button is None:
            parser.error("You must specify --button")
        if options.button not in buttons:
            parser.error("That button does not exist.")
        button = buttons[options.button]
        button.SetBacklight(options.button_backlight)

    if options.print_buttons:

        class PressReceiver(object):
            def __init__(self, button, name):
                self.button = button
                self.name = name

            def pressed(self):
                print self.name

        for name, btn in buttons.items():
            receiver = PressReceiver(btn, name)
            btn.connect_to_signal("Pressed", receiver.pressed)

        mainloop.run()

    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
