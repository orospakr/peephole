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

from peephole.drivers import buttons

VENDOR_ID = 0x04d8
DEVICE_ID = 0x0002

USB_INTERRUPTREAD_TIMEOUT = 4000

PICOLCD_CLEAR_CMD   = 0x94
PICOLCD_DISPLAY_CMD = 0x98
PICOLCD_SETFONT_CMD = 0x9C
PICOLCD_REPORT_INT_EE_WRITE = 0xA4
PICOLCD_GET_IRDATA = 0x21
PICOLCD_GET_KEYDATA = 0x11
PICOLCD_BACKLIGHT = 0x91
PICOLCD_SET_LED_STATE = 0x81

PICOLCD_KEYMAP = { 0x01: buttons.XK_plus,
                   0x02: buttons.XK_minus,
                   0x03: buttons.XK_F1,
                   0x04: buttons.XK_F2,
                   0x05: buttons.XK_F3,
                   0x06: buttons.XK_F4,
                   0x07: buttons.XK_F5,
                   0x0A: buttons.XK_Up,
                   0x08: buttons.XK_Left,
                   0x09: buttons.XK_Right,
                   0x0B: buttons.XK_Down,
                   0x0C: buttons.XK_Return
                   }
