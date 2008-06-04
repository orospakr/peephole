from pmock import *
import gobject

from tests.util import packet_fixture
from tests import *
from peephole.drivers.picolcd.picolcd import PicoLCD
from peephole.drivers.picolcd.button import Button
from peephole.drivers import buttons
from peephole.drivers.picolcd.consts import *

class ButtonsTest(MockTestCase):

    def setUp(self):
        self.picolcd = self.mock()
        self.picolcd.leds = [0, 0, 0, 0, 0, 0, 0]
        self.button = Button(self.picolcd, 'OK', buttons.XK_F1, 5)

    def testInstantiation(self):
        pass

    def testSetBacklight(self):
        self.picolcd.expects(once()).updateLeds()
        self.button.setBacklight(True)
        self.failUnlessEqual([0, 0, 0, 0, 0, 1, 0], self.picolcd.leds)
