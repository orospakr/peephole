#!/usr/bin/env python

# it may not be an ipod, but it's a good demo!

# hunks of code stolen from Andy Wingo's vumeter.py.

import gst
import gobject
import dbus
import dbus.mainloop.glib
import logging

def clamp(x, min, max):
    if x < min:
        return min
    elif x > max:
        return max
    return x

class Player(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        system_bus = dbus.SystemBus()
        proxy = system_bus.get_object('org.orospakr.peephole',
                                      '/org/orospakr/peephole/LCDs/PicoLCD')

    def run(self):
        try:
            s = 'alsasrc ! level message=true ! fakesink'
            pipeline = gst.parse_launch(s)
            self.set_sensitive(True)
            pipeline.get_bus().add_signal_watch()
            i = pipeline.get_bus().connect('message::element', self.on_message)
            pipeline.set_state(gst.STATE_PLAYING)
            gtk.Dialog.run(self)
            pipeline.get_bus().disconnect(i)
            pipeline.get_bus().remove_signal_watch()
            pipeline.set_state(gst.STATE_NULL)
        except gobject.GError, e:
            self.set_sensitive(True)
            self.error('Could not create pipeline', e.__str__)

        def error(self, message, secondary=None):
            logging.error(message)

        if secondary:
            m.format_secondary_text(secondary)
        m.run()

    def on_message(self, bus, message):
        if  message.structure.get_name() == 'level':
            s = message.structure
            for i in range(0, len(s['peak'])):
                #self.vus[i].freeze_notify()
                decay = clamp(s['decay'][i], -90.0, 0.0)
                peak = clamp(s['peak'][i], -90.0, 0.0)
                if peak > decay:
                    print "ERROR: peak bigger than decay!"

                #self.vus[i].set_property('decay', decay)
                #self.vus[i].set_property('peak', peak)

                # send to LCD!
        return True

if __name__ == "__main__":
    print("Simple Media player for Peephole.")



    player = Player()

