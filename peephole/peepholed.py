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

#  dbus-send --print-reply --type=method_call --system --dest='ca.infoglobe.peephole' /ca/infoglobe/peephole/LCDs/PicoLCD ca.infoglobe.peephole.LCD.DisplayText string:0 string:"stuffs"

import peephole.drivers.picolcd
import peephole.drivers.gtklcd
from peephole.dbus_lcd import DBusLCD
from peephole.dbus_peephole import DBusPeephole

PEEPHOLE_WELL_KNOWN_NAME = 'ca.infoglobe.peephole'

def main():
    print("Peephole.")

    logging.basicConfig(level=logging.DEBUG)

    gobject.threads_init()

    mainloop = gobject.MainLoop()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    system_bus = dbus.SystemBus()
    name = dbus.service.BusName(PEEPHOLE_WELL_KNOWN_NAME, system_bus)
    #my_lcd = peephole.drivers.picolcd.PicoLCD()

    lcds = []
    lcds += peephole.drivers.gtklcd.probe()
    lcds += peephole.drivers.picolcd.probe()

    if len(lcds) < 1:
        logging.error("No LCD devices available.")
        return -1
    dbus_lcds = []

    for lcd in lcds:
        logging.info("Initialising detected LCD: '%s'." % lcd.get_name())
        dbus_lcds.append(DBusLCD(lcd, system_bus, lcd.get_name()))
        lcd.start()
        lcd.clear()
        lcd.set_text("\x06\x05\x04\x03\x02\x01Peephole\x01\x02\x03\x04\x05\x06", 0, 0)
#         import time
#         for i in range(0, 12):
#             string1 = ""

#             begin = i * 20
#             if begin == 0:
#                 begin = 1
#             end = (i + 1) * 20

#             print "BEGIN AT : %s" % begin

#             for n in range(begin, end):
#                 string1 += chr(n)

#             print len(string1)

#             lcd.set_text(string1, 0, 0)
#             lcd.set_text(hex(begin) + "    ", 1, 0)

#             time.sleep(2)

        lcd.set_backlight(1)

    root_obj = DBusPeephole(dbus_lcds, system_bus)

    try:
        mainloop.run()
    except KeyboardInterrupt:
        # user pressed ^C, most likely.
        for lcd in lcds:
            lcd.stop()

if __name__ == "__main__":
    sys.exit(main())
