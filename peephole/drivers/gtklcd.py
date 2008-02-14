# coding: utf8
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
# crap, how do I detect lack of DISPLAY or gtk libs?

import peephole.drivers.driver

LCD_COLUMNS = 20
LCD_ROWS = 2

class LCDWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        panel_hbox = gtk.HBox()
        self.add(panel_hbox)
        panel_hbox.show()
        plusminusbox = gtk.VBox()
        panel_hbox.add(plusminusbox)
        plusminusbox.show()
        plus_button = gtk.Button("+")
        plusminusbox.add(plus_button)
        plus_button.show()
        minus_button = gtk.Button("-")
        plusminusbox.add(minus_button)
        minus_button.show()

        lcdvbox = gtk.VBox()
        #self.add(lcdvbox)
        panel_hbox.add(lcdvbox)
        lcdvbox.show()
        self.label = gtk.Label()
        lcdvbox.add(self.label)
        self.label.show()
        self.meter = gtk.ProgressBar()
        lcdvbox.add(self.meter)
        self.meter.show()

        directions_box = gtk.VBox()
        directions_box.show()
        panel_hbox.add(directions_box)
        up_button = gtk.Button(u"↑")
        up_button.show()
        directions_box.add(up_button)
        left_right_box = gtk.HBox()
        left_right_box.show()
        directions_box.add(left_right_box)
        left_button = gtk.Button(u"←")
        left_button.show()
        left_right_box.add(left_button)
        ok_button = gtk.Button("OK")
        ok_button.show()
        left_right_box.add(ok_button)
        right_button = gtk.Button(u"→")
        right_button.show()
        left_right_box.add(right_button)

        down_button = gtk.Button(u"↓")
        down_button.show()
        directions_box.add(down_button)

    def update(self, contents):
        #self.label.set_markup("")
        text = '<span font_family="monospace">'
        for line in contents:
            text = text + line + '\n'
        text += '</span>'
        self.label.set_markup(text)

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
        self.contents = [[' ' * LCD_COLUMNS] * LCD_ROWS][0] # not sure why python ends up wrapping it in an extra array, but it does what I expect otherwise! <3
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

    def get_name(self):
        return 'GTK'

