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

import peephole.drivers.button

class Button(peephole.drivers.button.Button):
    def __init__(self, picolcd, name, keysym, led_number):
        peephole.drivers.button.Button.__init__(self, picolcd, name, keysym)
        self.led_number = led_number

    def setBacklight(self, state):
        self.lcd.leds[self.led_number] = state
        self.lcd.updateLeds()
        peephole.drivers.button.Button.setBacklight(self, state)

