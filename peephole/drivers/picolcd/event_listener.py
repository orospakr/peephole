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

from peephole.util import IdleObject
import logging
from gettext import gettext as _
import gobject

# yes, I am polling instead of actually using asyncronous I/O.
# PyUSB doesn't support asynchronous operation, even though libusb
# has fairly comprehensive asynchronous support.
class EventListener(gobject.GObject):

    __gsignals__ = {
        'buttonPressed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_INT,))}

    def __init__(self, lcd):
        gobject.GObject.__init__(self)
        self.lcd = lcd
        self.please_stop = False
        self.timer = None

    def start(self):
        # register glib timeout
        self.timer = gobject.timeout_add(50, self.check_button_press)

    def check_button_press(self):
        button = self.lcd.get_event_nonblock()
        if button is not None:
            logging.debug("Button was: %s" % button)
            self.emit('buttonPressed', button)
        return True

#     def run(self):
#         '''This is what is run in the Thread when it is started.'''
#         logging.debug(_("PicoLCD button listener thread now running."))
#         while True:
#             if self.please_stop:
#                 return
#             button = self.lcd.get_event(self.check_if_time_to_stop)
#             if button is not None:
#                 logging.debug("Button was: %s" % button)
#                 self.emit('buttonPressed', button)

    def shutdown(self):
        # unregister glib timeout
        if self.timer is not None:
            gobject.source_remove(self.timer)
