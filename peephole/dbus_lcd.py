import gobject
from gettext import gettext as _
import dbus
import dbus.service
import dbus.mainloop.glib
import logging
import struct
import sys

LCD_INTERFACE = 'ca.infoglobe.peephole.LCD'

LCD_PATH_BASE = '/ca/infoglobe/peephole/LCDs/'


class DBusLCD(dbus.service.Object):
    '''Object exposing an LCD over D-Bus.

    lcd -- LCD object representing the actual hardware.

    bus_or_tube -- D-Bus bus or Telepathy Tube to publish this LCD over.

    device_name -- Friendly name for the device, for D-Bus path.
    '''

    def __init__(self, lcd, bus_or_tube, device_name):
        dbus.service.Object.__init__(self, bus_or_tube, LCD_PATH_BASE + device_name)
        self.path = device_name
        self.bus_or_tube = bus_or_tube
        self.lcd = lcd
        lcd.add_button_callback(self.ButtonPressed)
        #lcd.start_button_listener()

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='is', out_signature='')
    def DisplayText(self, line_number, text):
        logging.debug(_("User asked to display: %s") % text)
        self.lcd.set_text(str(text), int(line_number), 0)

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='', out_signature='i')
    def GetLines(self):
        self.lcd.get_lines()

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='d', out_signature='')
    def DrawVUMeter(self, value):
        self.lcd.draw_meter(value)

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='', out_signature='')
    def Clear(self):
        self.lcd.clear()

    @dbus.service.signal(dbus_interface=LCD_INTERFACE,
                         signature='i')
    def ButtonPressed(self, button):
        pass

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='b', out_signature='')
    def SetBacklight(self, status):
        self.lcd.set_backlight(status)

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='ai', out_signature='')
    def SetLEDs(self, leds):
        self.lcd.set_leds(leds)