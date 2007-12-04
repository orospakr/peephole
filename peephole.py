#!/usr/bin/env python

import gobject
from gettext import gettext as _
import dbus
import dbus.service
import dbus.mainloop.glib
import logging
import struct
import sys
import time
import threading
import usb

#  dbus-send --print-reply --type=method_call --system --dest='org.orospakr.peephole' /org/orospakr/peephole/LCDs/PicoLCD org.orospakr.peephole.LCD.DisplayText string:0 string:"stuffs"

LCD_INTERFACE = 'org.orospakr.peephole.LCD'
PEEPHOLE_WELL_KNOWN_NAME = 'org.orospakr.peephole'
LCD_PATH_BASE = '/org/orospakr/peephole/LCDs/'

def get_usb_device(vendor_id, device_id):
    buses = usb.busses()
    for bus in buses:
        for device in bus.devices:
            if device.idVendor == vendor_id and device.idProduct == device_id:
                return device
    return None

class PicoLCDButtonListener(threading.Thread):
    def __init__(self, lcd, button_cb):
        threading.Thread.__init__(self)
        self.lcd = lcd
        self.lock = threading.Lock()
        self.button_cb = button_cb
        self.please_stop = False

    def run(self):
        '''This is what is run in the Thread when it is started.'''
        print "lol, internet"
        while True:
            self.lock.acquire()
            if self.please_stop:
                return
            button = self.lcd.get_button()
            if self.button_cb is not None:
                self.button_cb(button)
            self.lock.release()

    def stop(self):
        '''Called by the main thread to stop the this button listener thread.'''
        self.lock.acquire()
        self.please_stop = True
        self.lock.release()

class PicoLCDHardware(object):
    '''Wraps the USB connectivity for the PicoLCD 20x2 device.'''

    # USB device IDs
    VENDOR_ID = 0x04d8
    DEVICE_ID = 0x0002

    def __init__(self):
        self.lcd_device = get_usb_device(self.VENDOR_ID, self.DEVICE_ID)
        if self.lcd_device is None:
            sys.exit(_("PicoLCD not found."))
        self.lcd_handle = self.lcd_device.open()
        try:
            self.lcd_handle.detachKernelDriver(0)
        except usb.USBError, e:
            print _("Could not detach kernel driver.")
        self.lcd_configuration = self.lcd_device.configurations[0]
        print("%s" % self.lcd_device.configurations[0])
        self.lcd_handle.setConfiguration(self.lcd_configuration)
        time.sleep(0.009) # for shame

        # we know it's the first interface's only option (there are
        # no alternate interfaces)
        self.lcd_interface = self.lcd_configuration.interfaces[0][0]
        #self.lcd_handle.detachKernelDriver(self.lcd_interface)
        interface = self.lcd_handle.claimInterface(self.lcd_interface)
        interface_alt = self.lcd_handle.setAltInterface(self.lcd_interface)

        self.lcd_interface = self.lcd_configuration.interfaces[0][0]
        time.sleep(1) # also for shame
        #self.start_button_listener()

    def write_command(self, packet):
        endp = self.lcd_interface.endpoints[1]
        self.lcd_handle.interruptWrite(endp.address, packet, 1000)

    def get_button(self):
        '''Blocks until a button down event is detected, and returns it.'''
        endp = self.lcd_interface.endpoints[0]
        while True:
            print("Re-running interruptRead loop...")
            try:
                packet = self.lcd_handle.interruptRead(endp.address, 24, 10000)
            except usb.USBError: # it throws an exception if the timeout is hit.
                continue
            if packet[0] == 0x11:
                if packet[1] == 0:
                    continue
                print("Button pressed: x%02x" % packet[1])
                return packet[1]


class PicoLCD(object):
    '''Represents a picoLCD device.'''
    PICOLCD_DISPLAY_CMD = 0x98
    PICOLCD_SETFONT_CMD = 0x9C

    def generate_text_packet(self, text, row, col):
        assert(len(text) < 256)
        fmt = 'BBBB%is' % len(text)
        return struct.pack(fmt, self.PICOLCD_DISPLAY_CMD, row, col, len(text), text)

    def write_char(self):
        '''Writes a test char into the CG RAM (Character Generation RAM) of the 
        device.'''
        char_id = 0
        packet = struct.pack('B', self.PICOLCD_SETFONT_CMD, char_id, )
        self.lcd.write_command
        
    def __init__(self):
        pass

    def start(self):
        '''We have this logic started separately from the class constructor,
        so this class can be instantiated by the test suite.'''
        self.lcd = PicoLCDHardware()

    def set_text(self, text, row, col):
        packet = self.generate_text_packet(text, row, col)
        self.lcd.write_command(packet)

    def start_button_listener(self):
        logging.warn(_("Starting button listener thread."))
        #self.lock = threading.Lock()
        #self.listener_thread = threading.Thread(target=self.button_listener)
        #self.listener_thread.start()

        self.listener_thread = PicoLCDButtonListener(self.lcd, self.button_cb)
        self.listener_thread.start()
        time.sleep(3)
        logging.warn(_("Thread started."))

    def get_lines(self):
        '''The PicoLCD 20x2 always has two lines -- whoda thunk it.'''
        return 2

    def stop(self):
        '''Stop the driver.'''
        self.listener_thread.stop()
        self.listener_thread.join()

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
        lcd.button_cb = self.ButtonPressed
        lcd.start_button_listener()

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='is', out_signature='')
    def DisplayText(self, line_number, text):
        print _("User asked to display: %s") % text
        self.lcd.set_text(str(text), int(line_number), 0)

    @dbus.service.method(dbus_interface=LCD_INTERFACE,
                         in_signature='', out_signature='i')
    def GetLines(self):
        self.lcd.get_lines()

    @dbus.service.signal(dbus_interface=LCD_INTERFACE,
                         signature='i')
    def ButtonPressed(self, button):
        pass

if __name__ == "__main__":

    gobject.threads_init()

    mainloop = gobject.MainLoop()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    system_bus = dbus.SystemBus()
    name = dbus.service.BusName(PEEPHOLE_WELL_KNOWN_NAME, system_bus)
    my_lcd = PicoLCD()
    my_lcd.start()
    my_lcd.set_text("\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09whee", 0, 0)
    # while True:
    #     my_lcd.get_button()
    object = DBusLCD(my_lcd, system_bus, 'PicoLCD')

    try:
        mainloop.run()
    except KeyboardInterrupt:
        # program is now quitting, so...
        my_lcd.stop()
