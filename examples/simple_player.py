#!/usr/bin/env python

# it may not be an ipod, but it's a good demo!

# hunks of code stolen from Andy Wingo's (f)vumeter.py.

import pygst
import gst
import gobject
import dbus
import dbus.mainloop.glib
import logging
import sys

def iec_scale(db):
    '''Returns the meter deflection percentage given a dB value.'''
    pct = 0.0
    if db < -70.0:
        pct = 0.0
    elif db < -60.0:
        pct = (db + 70.0) * 0.25
    elif db < -50.0:
        pct = (db + 60.0) * 0.5 + 2.5
    elif db < -40.0:
        pct = (db + 50.0) * 0.75 + 7.5
    elif db < -30.0:
        pct = (db + 40.0) * 1.5 + 15.0
    elif db < -20.0:
        pct = (db + 30.0) * 2.0 + 30.0
    elif db < 0.0:
        pct = (db + 20.0) * 2.5 + 50.0
    else:
        pct = 100.0
    return pct

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
        self.xlcd = system_bus.get_object('ca.infoglobe.peephole',
                                         '/ca/infoglobe/peephole/LCDs/PicoLCD')
        self.lcd = dbus.Interface(self.xlcd, dbus_interface='ca.infoglobe.peephole.LCD')

    def run(self):
        try:
            # gst-launch filesrc location=enjoy-the-silence.mp3 ! mad ! audioconvert ! audioresample ! alsasink
            s = 'filesrc location=enjoy-the-silence.mp3 ! mad ! audioconvert ! audioresample ! level message=true !alsasink'
            pipeline = gst.parse_launch(s)
            #self.set_sensitive(True)
            pipeline.get_bus().add_signal_watch()
            i = pipeline.get_bus().connect('message::element', self.on_message)
            pipeline.set_state(gst.STATE_PLAYING)
            logging.debug("Now starting glib mainloop...")
            gobject.MainLoop().run()
            pipeline.get_bus().disconnect(i)
            pipeline.get_bus().remove_signal_watch()
            pipeline.set_state(gst.STATE_NULL)
        except gobject.GError, e:
            #self.set_sensitive(True)
            self.error('Could not create pipeline', e.__str__)

    def error(self, message, secondary=None):
        logging.error(message)

        if secondary:
            logging.error("... secondary.")

    def on_message(self, bus, message ):
        logging.debug(str(message))
        if get_name_func() == 'level':
            s = message.structure
            logging.debug("len is %i" % len(s['peak']))

            for i in range(0, len(s['peak'])):
                #self.vus[i].freeze_notify()
                logging.debug(s['decay'][i])
                decay = clamp(s['decay'][i], -90.0, 0.0)
                peak = clamp(s['peak'][i], -90.0, 0.0)
                if peak > decay:
                    print "ERROR: peak bigger than decay!"

                #self.vus[i].set_property('decay', decay)
                #self.vus[i].set_property('peak', peak)
                print (iec_scale(decay))/100
                self.lcd.DrawVUMeter(((iec_scale(peak))/100))
            # sys.exit()

                # send to LCD!
        return True

if __name__ == "__main__":
    print("Simple Media player for Peephole.")

    logging.basicConfig(level=logging.DEBUG)

    player = Player()
    player.run()

    #gobject.MainLoop().run()

