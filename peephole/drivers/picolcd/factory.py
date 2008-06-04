from peephole.drivers.picolcd.event_listener import EventListener
from peephole.drivers.picolcd.device import Device
from peephole.drivers.picolcd.vu_meter import VUMeter
from peephole.drivers.picolcd.button import Button

class Factory(object):
    def makeEventListener(self, device):
       return EventListener(device)

    def makeDevice(self, usb_device):
        return Hardware(usb_device)

    def makeVUMeter(self, picolcd):
        return VUMeter(picolcd)

    def makeButton(self, lcd, name, keysym):
        return Button(lcd, name, keysym)

    def makeButtons(self, lcd, button_names_and_keysyms_and_leds):
        result = []
        for (name, keysym_and_led) in button_names_and_keysyms_and_leds.items():
            keysym, led = keysym_and_led
            result.append(Button(lcd, name, keysym, led))
