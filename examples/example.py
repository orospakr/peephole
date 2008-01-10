#!/usr/bin/env python

import dbus

def button_pressed_callback(self, button):
    print "Button %i pressed!"

bus = dbus.SystemBus()

proxy = bus.get_object('org.orospakr.peephole',
                       '/org/orospakr/peephole/LCDs/PicoLCD')
lcd = dbus.Interface(proxy, dbus_interface='org.orospakr.peephole.LCD')

lcd.Clear()
lcd.DisplayText(0, "Hello!")

lcd.connect("ButtonPressed", button_pressed_callback)





