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
from peephole.drivers.button import Button

LCD_COLUMNS = 20
LCD_ROWS = 2

def probe():
    # there's only ever one, so just instantiate it
    # and return it.
    if display_available is not True:
        return []
    lcd = GTK()
    return [lcd]

class LCDButtonWidget(gtk.Button):
    def __init__(self, lcd_button, custom_text=None):
        self.lcd_button = lcd_button
        if custom_text is None:
            gtk.Button.__init__(self, lcd_button.name)
        else:
            gtk.Button.__init__(self, custom_text)
        self.lcd_button.registerBacklightCallback(self.setBacklight)
        self.connect("clicked", self.onClicked, None)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("grey"))

    def setBacklight(self, state):
        if state == True:
            self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("green"))
        else:
            self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("grey"))

    def onClicked(self, widget, data=None):
        self.lcd_button.pressed()

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
        plus_button = LCDButtonWidget(self.gtklcd.plus_button, '+')
        plusminusbox.add(plus_button)
        minus_button = LCDButtonWidget(self.gtklcd.minus_button, '-')
        plusminusbox.add(minus_button)

        lcdvbox = gtk.VBox()

        panel_hbox.add(lcdvbox)
        lcdvbox.show()
        self.label = gtk.Label()
        lcdvbox.add(self.label)
        self.label.show()

        fbuttons_hbox = gtk.HBox()
        lcdvbox.add(fbuttons_hbox)

        f1button = LCDButtonWidget(self.gtklcd.f1_button)
        fbuttons_hbox.add(f1button)

        f2button = LCDButtonWidget(self.gtklcd.f2_button)
        fbuttons_hbox.add(f2button)

        f3button = LCDButtonWidget(self.gtklcd.f3_button)
        fbuttons_hbox.add(f3button)

        f4button = LCDButtonWidget(self.gtklcd.f4_button)
        fbuttons_hbox.add(f4button)

        f5button = LCDButtonWidget(self.gtklcd.f5_button)
        fbuttons_hbox.add(f5button)

        self.meter = gtk.ProgressBar()
        self.meter.set_orientation(gtk.PROGRESS_BOTTOM_TO_TOP)
        panel_hbox.add(self.meter)

        directions_box = gtk.VBox()
        panel_hbox.add(directions_box)

        up_button = LCDButtonWidget(self.gtklcd.up_button, u"↑")
        directions_box.add(up_button)

        left_right_box = gtk.HBox()
        left_right_box.show()
        directions_box.add(left_right_box)

        left_button = LCDButtonWidget(self.gtklcd.left_button, u"←")
        left_right_box.add(left_button)

        ok_button = LCDButtonWidget(self.gtklcd.return_button, "OK")
        left_right_box.add(ok_button)

        right_button = LCDButtonWidget(self.gtklcd.right_button, u"→")
        left_right_box.add(right_button)

        down_button =LCDButtonWidget(self.gtklcd.down_button, u"↓")
        directions_box.add(down_button)

        self.show_all()

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

        self.return_button = Button(self, 'Return', buttons.XK_Return)
        self.addButton(self.return_button)

        self.plus_button = Button(self, 'Plus', buttons.XK_plus)
        self.addButton(self.plus_button)

        self.minus_button = Button(self, 'Minus', buttons.XK_minus)
        self.addButton(self.minus_button)

        self.f1_button = Button(self, 'F1', buttons.XK_F1)
        self.addButton(self.f1_button)

        self.f2_button = Button(self, 'F2', buttons.XK_F2)
        self.addButton(self.f2_button)

        self.f3_button = Button(self, 'F3', buttons.XK_F3)
        self.addButton(self.f3_button)

        self.f4_button = Button(self, 'F4', buttons.XK_F4)
        self.addButton(self.f4_button)

        self.f5_button = Button(self, 'F5', buttons.XK_F5)
        self.addButton(self.f5_button)

        self.up_button = Button(self, 'Up', buttons.XK_Up)
        self.addButton(self.up_button)

        self.down_button = Button(self, 'Down', buttons.XK_Down)
        self.addButton(self.down_button)

        self.left_button = Button(self, 'Left', buttons.XK_Left)
        self.addButton(self.left_button)

        self.right_button = Button(self, 'Right', buttons.XK_Right)
        self.addButton(self.right_button)

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
