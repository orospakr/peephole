# Peephole - a D-Bus service providing access to small LCD panels
# Copyright (C) 2007-2008 Andrew Clunis

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from peephole.drivers.picolcd.event_listener import EventListener
from peephole.drivers.picolcd.device import Device
from peephole.drivers.picolcd.vu_meter import VUMeter
from peephole.drivers.picolcd.button import Button

class Factory(object):
    def makeEventListener(self, device):
       return EventListener(device)

    def makeDevice(self, usb_device):
        return Device(usb_device)

    def makeVUMeter(self, picolcd):
        return VUMeter(picolcd)

    def makeButton(self, lcd, name, keysym):
        return Button(lcd, name, keysym)

    def makeButtons(self, lcd, button_names_and_keysyms_and_leds):
        result = []
        for (name, keysym_and_led) in button_names_and_keysyms_and_leds.items():
            keysym, led = keysym_and_led
            result.append(Button(lcd, name, keysym, led))
        return result
