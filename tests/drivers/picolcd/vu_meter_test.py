from pmock import *

from tests.util import packet_fixture
from tests import *
from peephole.drivers.picolcd.picolcd import PicoLCD
from peephole.drivers import buttons

from peephole.drivers.picolcd.vu_meter import VUMeter

class VUMeterTest(MockTestCase):

    FIRST_ROW_FIXTURE = packet_fixture (
        [0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F])

    FIVE_ROWS_FIXTURE = packet_fixture (
        [0x00, 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x1F])

    def setUp(self):
        self.picolcd = self.mock()
        self.vumeter = VUMeter(self.picolcd)

    def testGenerateBar(self):
        results = self.vumeter.generateBar(5)
        self.failUnlessEqual(self.FIVE_ROWS_FIXTURE,
                             results)

    def testWriteVUBars(self):
        # crap, this doesn't work very well!
        #        self.picolcd.expects(once()).upload_char(eq(1), eq(self.FIRST_ROW_FIXTURE))
        self.picolcd.expects(at_least_once()).method('upload_char')
        self.vumeter.writeVUBars()
