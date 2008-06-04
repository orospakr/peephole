from peephole.drivers.picolcd.event_listener import EventListener
from peephole.drivers.picolcd.device import Device
from peephole.drivers.picolcd.vu_meter import VUMeter
from peephole.drivers.button import Button

class Factory(object):
    def makeEventListener(self, device):
       return EventListener(device)

    def makeDevice(self, usb_device):
        return Hardware(usb_device)

    def makeVUMeter(self, picolcd):
        return VUMeter(picolcd)

    def makeButton(self, lcd, name, keysym):
        return Button(lcd, name, keysym)

    def makeButtons(self, lcd, button_names_and_keysyms):
        result = []
        for (name, keysym) in button_names_and_keysyms.items():
            result.append(Button(lcd, name, keysym))
