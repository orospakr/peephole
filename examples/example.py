#!/usr/bin/env python

import dbus

def button_pressed_callback(self, button):
    print "Button %i pressed!"

bus = dbus.SystemBus()

proxy = bus.get_object('ca.infoglobe.peephole',
                       '/ca/infoglobe/peephole/LCDs/PicoLCD')
lcd = dbus.Interface(proxy, dbus_interface='ca.infoglobe.peephole.LCD')

lcd.Clear()
lcd.DisplayText(0, "Hello!")

lcd.connect_to_signal("ButtonPressed", button_pressed_callback)





