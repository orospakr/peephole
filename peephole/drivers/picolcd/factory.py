from peephole.drivers.picolcd.event_listener import EventListener
from peephole.drivers.picolcd.device import Device
from peephole.drivers.picolcd.vu_meter import VUMeter

class Factory(object):
    def makeEventListener(self, device):
       return EventListener(device)

    def makeDevice(self, usb_device):
        return Hardware(usb_device)

    def makeVUMeter(self, picolcd):
        return VUMeter(picolcd)
