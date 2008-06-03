import unittest

import struct
import pmock
from pmock import *
import gobject

from tests.util import packet_fixture
import peephole.drivers.picolcd
from peephole.drivers import buttons

from peephole.drivers.picolcd.event_listener import EventListener

class EventListenerTest(MockTestCase):
    def testInstantiate(self):
        self.lcd_hardware = self.mock()
        EventListener(self.lcd_hardware)
