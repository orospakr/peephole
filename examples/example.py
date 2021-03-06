#!/usr/bin/env python

import dbus
import dbus.mainloop
import dbus.mainloop.glib
import gobject
import os
import time

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
mainloop = gobject.MainLoop()
bus = dbus.SystemBus()

proxy = bus.get_object('ca.infoglobe.peephole',
                       '/ca/infoglobe/peephole/LCDs/PicoLCD')
lcd = dbus.Interface(proxy, dbus_interface='ca.infoglobe.peephole.LCD')

lcd.Clear()


import time

for i in range(0, 12):
    string1 = ""

    begin = i * 20
    if begin == 0:
        begin = 1
    end = (i + 1) * 20

    print "BEGIN AT : %s" % begin

    for n in range(begin, end):
        string1 += chr(n)

    print len(string1)

    lcd.DisplayText(0, string1)
    lcd.DisplayText(1, hex(begin) + "    ")

    time.sleep(2)

bprox = bus.get_object('ca.infoglobe.peephole',
                       '/ca/infoglobe/peephole/LCDs/PicoLCD/Buttons/F1')

button = dbus.Interface(bprox, dbus_interface='ca.infoglobe.peephole.Button')

def button_pressed_callback():
    button.SetBacklight(True)
    time.sleep(0.1)
    button.SetBacklight(False)

#while True:
#    button.SetBacklight(True)
#    button.SetBacklight(False)

#lcd.connect_to_signal("ButtonPressed", button_pressed_callback)
button.connect_to_signal("Pressed", button_pressed_callback)

mainloop.run()
