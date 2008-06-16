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

from peephole.util import virtual

class Button(object):
    def __init__(self, lcd, name, keysym):
        self.name = name
        self.lcd = lcd
        self.keysym = keysym
        self.pressed_cbs = []
        self.backlight_cbs = []

    def setBacklight(self, state):
        for cb in self.backlight_cbs:
            cb(state)

    def registerBacklightCallback(self, cb):
        self.backlight_cbs.append(cb)

    def registerPressedCallback(self, cb):
        self.pressed_cbs.append(cb)

    def pressed(self):
        for cb in self.pressed_cbs:
            cb()
        # for folks using the old API...
        self.lcd.fire_btn_cb(self.keysym)
