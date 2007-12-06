#!/usr/bin/env python

# it may not be an ipod, but it's a good demo!

# hunks of code stolen from Andy Wingo's vumeter.py.

import pygst
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

def scale_to_lcd(value):
    '''Scales the VU meter value to something in between 1 and 0.'''
    return (value * -1) / 50

class Player(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        system_bus = dbus.SystemBus()
        self.lcd = system_bus.get_object('org.orospakr.peephole',
                                         '/org/orospakr/peephole/LCDs/PicoLCD')

    def run(self):
        try:
            # gst-launch filesrc location=Music47.mp3 ! mad ! audioconvert ! audioresample ! alsasink
            s = 'filesrc location=Music47.mp3 ! mad ! audioconvert ! audioresample ! level message=true !alsasink'
            pipeline = gst.parse_launch(s)
            #self.set_sensitive(True)
            pipeline.get_bus().add_signal_watch()
            i = pipeline.get_bus().connect('message::element', self.on_message)
            pipeline.set_state(gst.STATE_PLAYING)
            gobject.MainLoop().run()
            pipeline.get_bus().disconnect(i)
            pipeline.get_bus().remove_signal_watch()
            pipeline.set_state(gst.STATE_NULL)
        except gobject.GError, e:
            raise e
            #self.set_sensitive(True)
            self.error('Could not create pipeline', e.__str__)

    def error(self, message, secondary=None):
        logging.error(message)

        if secondary:
            logging.error("... secondary.")

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
                self.lcd.DrawVUMeter(scale_to_lcd(peak))

                # send to LCD!
        return True

if __name__ == "__main__":
    print("Simple Media player for Peephole.")



    player = Player()
    player.run()

    #gobject.MainLoop().run()

