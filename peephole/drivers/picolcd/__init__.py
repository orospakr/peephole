import peephole.drivers.driver
from peephole.drivers.picolcd.picolcd import PicoLCD

from peephole.drivers.picolcd.consts import *

def probe():
    '''Returns PicoLCD objects for all the PicoLCDs found on
    the system.'''

    lcd_device = peephole.drivers.driver.get_usb_device(VENDOR_ID, DEVICE_ID)
    if lcd_device is None:
        return []
    else:
        pico = PicoLCD(lcd_device)
        return [pico]
