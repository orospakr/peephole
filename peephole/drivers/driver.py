import usb
from gettext import gettext as _

def get_usb_device(vendor_id, device_id):
    buses = usb.busses()
    for bus in buses:
        for device in bus.devices:
            if device.idVendor == vendor_id and device.idProduct == device_id:
                return device
    return None

class Driver(object):
    def __init__(self):
        pass
