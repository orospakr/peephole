#!/usr/bin/env python

import gobject
from gettext import gettext as _
import dbus
import dbus.service
import dbus.mainloop.glib
import logging
import struct
import sys
import os
from optparse import OptionParser

from peephole.peepholed import PEEPHOLE_WELL_KNOWN_NAME
from peephole.dbus_settings import *

def main():
    print "Peephole client."
    usage = ""
    parser = OptionParser()
    parser.add_option("-L", "--lcd", dest="lcd",
                      help="LCD to interact with")
    parser.add_option("-l", "--list", action="store_true",
                      dest="list",
                      help="Print list of LCDs in the system")
    parser.add_option("-b", "--print-buttons", action="store_true",
                      dest="print_buttons",
                      help="Print button events on stdout as they occur")
    parser.add_option("-s", "--send-events", action="store_true",
                      dest="send_events",
                      help="Wait for input commands (set backlight) on stdin")

    (options, args) = parser.parse_args()


    mainloop = gobject.MainLoop()
    bus = dbus.SystemBus()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    peep_proxy = bus.get_object(PEEPHOLE_WELL_KNOWN_NAME,
                                PEEPHOLE_PATH)

    peep = dbus.Interface(peep_proxy, dbus_interface=PEEPHOLE_INTERFACE)

    lcd_paths = peep.GetLCDs()
    lcds = {}

    for path in lcd_paths:
        lcd_proxy = bus.get_object(PEEPHOLE_WELL_KNOWN_NAME, path)
        lcd = dbus.Interface(lcd_proxy, dbus_interface=LCD_INTERFACE)
        lcd_name = lcd.GetName()
        lcds[lcd_name] = lcd

    if options.list:
        for name, lcd in lcds.items():
            print name

    selected_lcd = None
    if options.lcd is not None:
        if options.lcd not in lcds:
            print "That LCD does not exist."
            sys.exit(-1)
        selected_lcd = lcds[options.lcd]
        print "Selected: '%s'" % options.lcd
    else:
        for name, l in lcds.items():
            print "Fell back to default LCD: '%s'" % name
            selected_lcd = l
            break

    if options.send_events:
        button_paths = []
        buttons = {}
        button_paths = selected_lcd.GetButtons()
        for path in button_paths:
            button_proxy = bus.get_object(PEEPHOLE_WELL_KNOWN_NAME, path)
            button = dbus.Interface(button_proxy, dbus_interface=BUTTON_INTERFACE)
            button_name = button.GetName()
            buttons[button_name] = button

        while True:
            s = sys.stdin.readline()
            if not s:
                break
            items = s.split()
            if items[0] == 'SetBacklight':
                if items[2] == 'True':
                    buttons[items[1]].SetBacklight(True)
                else:
                    buttons[items[1]].SetBacklight(False)
            if items[0] == 'SetText':
                pass
        sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
