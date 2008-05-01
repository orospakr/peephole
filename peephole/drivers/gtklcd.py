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

display_available = True

try:
    import pygtk
    pygtk.require('2.0')
except ImportError:
    display_available = False

import warnings
warnings.filterwarnings('error', module='gtk')
try:
    try:
        import gtk
    except ImportError:
        display_available = False
except Warning, e:
    display_available = False
warnings.resetwarnings()

if display_available:
    import gtk
else:
    class gtk:
        class Window:
            pass
    

import logging

import peephole.drivers.driver
from peephole.drivers import buttons

LCD_COLUMNS = 20
LCD_ROWS = 2

def probe():
    # there's only ever one, so just instantiate it
    # and return it.
    if display_available is not True:
        return []
    lcd = GTK()
    return [lcd]

class LCDWindow(gtk.Window):
    def __init__(self, gtklcd):
        self.gtklcd = gtklcd
        gtk.Window.__init__(self)
        self.set_title("Peephole GTK")
        panel_hbox = gtk.HBox()
        self.add(panel_hbox)
        panel_hbox.show()
        plusminusbox = gtk.VBox()
        panel_hbox.add(plusminusbox)
        plusminusbox.show()
        plus_button = gtk.Button("+")
        plus_button.connect("clicked", self.plus_button_clicked, None)
        plusminusbox.add(plus_button)
        plus_button.show()
        minus_button = gtk.Button("-")
        minus_button.connect("clicked", self.minus_button_clicked, None)
        plusminusbox.add(minus_button)
        minus_button.show()

        lcdvbox = gtk.VBox()
        #self.add(lcdvbox)
        panel_hbox.add(lcdvbox)
        lcdvbox.show()
        self.label = gtk.Label()
        lcdvbox.add(self.label)
        self.label.show()

        fbuttons_hbox = gtk.HBox()
        fbuttons_hbox.show()
        lcdvbox.add(fbuttons_hbox)

        f1button = gtk.Button("F1")
        f1button.connect("clicked", self.f1_button_clicked, None)
        f1button.show()
        fbuttons_hbox.add(f1button)
        f2button = gtk.Button("F2")
        f2button.connect("clicked", self.f2_button_clicked, None)
        f2button.show()
        fbuttons_hbox.add(f2button)
        f3button = gtk.Button("F3")
        f3button.connect("clicked", self.f3_button_clicked, None)
        f3button.show()
        fbuttons_hbox.add(f3button)
        f4button = gtk.Button("F4")
        f4button.connect("clicked", self.f4_button_clicked, None)
        f4button.show()
        fbuttons_hbox.add(f4button)
        f5button = gtk.Button("F5")
        f5button.connect("clicked", self.f5_button_clicked, None)
        f5button.show()
        fbuttons_hbox.add(f5button)

        self.meter = gtk.ProgressBar()
        self.meter.set_orientation(gtk.PROGRESS_BOTTOM_TO_TOP)
        panel_hbox.add(self.meter)
        self.meter.show()

        directions_box = gtk.VBox()
        directions_box.show()
        panel_hbox.add(directions_box)
        up_button = gtk.Button(u"↑")
        up_button.connect("clicked", self.up_button_clicked, None)
        up_button.show()
        directions_box.add(up_button)
        left_right_box = gtk.HBox()
        left_right_box.show()
        directions_box.add(left_right_box)
        left_button = gtk.Button(u"←")
        left_button.connect("clicked", self.left_button_clicked, None)
        left_button.show()
        left_right_box.add(left_button)
        ok_button = gtk.Button("OK")

        ok_button.show()
        ok_button.connect("clicked", self.ok_button_clicked, None)
        left_right_box.add(ok_button)
        right_button = gtk.Button(u"→")
        right_button.connect("clicked", self.right_button_clicked, None)
        right_button.show()
        left_right_box.add(right_button)

        down_button = gtk.Button(u"↓")
        down_button.connect("clicked", self.down_button_clicked, None)
        down_button.show()
        directions_box.add(down_button)

    def ok_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_Return)

    def plus_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_plus)

    def minus_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_minus)

    def f1_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_F1)

    def f2_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_F2)

    def f3_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_F3)

    def f4_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_F4)

    def f5_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_F5)

    def up_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_Up)

    def down_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_Down)

    def left_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_Left)

    def right_button_clicked(self, widget, data=None):
        self.gtklcd.fire_btn_cb(buttons.XK_Right)

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

    def __init__(self):
        self.clear()
        peephole.drivers.driver.Driver.__init__(self)

    def start(self):
        self.window = LCDWindow(self)
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

