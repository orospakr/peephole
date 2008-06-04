from peephole.util import IdleObject
import threading
import logging
from gettext import gettext as _
import gobject

class EventListener(threading.Thread, IdleObject):

    __gsignals__ = {
        'buttonPressed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_INT,))}

    def __init__(self, lcd):
        threading.Thread.__init__(self)
        IdleObject.__init__(self)
        self.lcd = lcd
        self.please_stop = False

    def check_if_time_to_stop(self):
        return self.please_stop

    def run(self):
        '''This is what is run in the Thread when it is started.'''
        logging.debug(_("PicoLCD button listener thread now running."))
        while True:
            if self.please_stop:
                return
            button = self.lcd.get_event(self.check_if_time_to_stop)
            if button is not None:
                logging.debug("Button was: %s" % button)
                self.emit('buttonPressed', button)

    def shutdown(self):
        '''Called by the main thread to stop the this button listener thread.'''
        self.please_stop = True
