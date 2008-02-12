# Peephole - A D-Bus service for LCD displays
# Copyright (C) 2007, 2008 Infoglobe

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

import pygtk
pygtk.require('2.0')
import gtk

import peephole.drivers.driver

LCD_COLUMNS = 20
LCD_ROWS = 2

class LCDWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        hbox = gtk.VBox()
        self.add(hbox)
        hbox.show()
        self.label = gtk.Label()
        hbox.add(self.label)
        self.label.show()
        self.meter = gtk.ProgressBar()
        hbox.add(self.meter)
        self.meter.show()

    def update(self, contents):
        self.label.set_text("")
        for line in contents:
            self.label.set_text(self.label.get_text() + "\n" + line)

    def update_meter(self, fraction):
        self.meter.set_fraction(fraction)

class GTK(peephole.drivers.driver.Driver):
    '''Represents a GTK window as an LCD driver device.

    This is *really easy* because Peephole already has a running
    glib event loop.'''

    button_cbs = []

    def __init__(self):
        self.clear()
        peephole.drivers.driver.Driver.__init__(self)

    def start(self):
        self.window = LCDWindow()
        self.window.show()

    def stop(self):
        self.window.destroy()

    def clear(self):
        self.contents = [[' ' * LCD_COLUMNS] * LCD_ROWS][0]
        # also refresh LCDWindow...

    def set_backlight(self, status):
        # I could change the background color of the LCDWindow...
        pass

    def set_text(self, text, row, col):
        if row > LCD_ROWS-1: # -1 because row is zero-based, while LCD_ROWS is a count and therefore not
            raise ValueError("The GTK LCD driver only has %i rows, and you asked for row #%d (zero-based)." % (LCD_ROWS, row))

        new_row = peephole.drivers.driver.replace_text(self.contents[row],
                                                       text, col, LCD_COLUMNS)
        self.contents[row] = new_row[:LCD_COLUMNS]
        assert len(self.contents[row]) == LCD_COLUMNS
        self.window.update(self.contents)

    def draw_meter(self, value):
        self.window.update_meter(value)


