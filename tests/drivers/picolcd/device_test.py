import unittest

import struct
import pmock
from pmock import *
import gobject

from tests.util import packet_fixture
import peephole.drivers.picolcd.device
from peephole.drivers import buttons

class DeviceTest(pmock.MockTestCase):
    def setUp(self):
        self.picolcd_usb = self.mock()
        self.picolcd_handle = self.mock()
        self.picolcd_configuration = self.mock()
        self.picolcd_usb.expects(pmock.once()).open().will(pmock.return_value(self.picolcd_handle))
        self.picolcd_configuration = self.mock()
        self.picolcd_interface = self.mock()
        self.picolcd_configuration.interfaces = [ [ self.picolcd_interface ] ]
        self.picolcd_usb.configurations = [self.picolcd_configuration]
        self.picolcd_handle.expects(pmock.once()).detachKernelDriver(pmock.eq(0))
        self.picolcd_handle.expects(pmock.once()).setConfiguration(pmock.same(self.picolcd_configuration))
        self.picolcd_handle.expects(pmock.once()).claimInterface(pmock.same(self.picolcd_interface))
        self.picolcd_handle.expects(pmock.once()).setAltInterface(pmock.same(self.picolcd_interface))
        self.hw = peephole.drivers.picolcd.device.Device(self.picolcd_usb)

    def testInstantiate(self):
        self.failIfEqual(None, self.hw)

    def sendEvent(self, packet):
        endpoint = self.mock()
        endpoint.address = 2
        self.one_run_completed = False
        self.picolcd_interface.endpoints = [endpoint]
        def should_i_stop():
            if self.one_run_completed:
                return True
            else:
                self.one_run_completed = True
                return False
        self.picolcd_handle.expects(pmock.once()).interruptRead(pmock.eq(2), pmock.eq(24), pmock.eq(4000)).will(pmock.return_value(packet))
        return self.hw.get_event(should_i_stop)

    def testReceiveButtonEvent(self):
        packet = [0x11, 0x04, 0x00]
        button_result = self.sendEvent(packet)
        self.failUnlessEqual(button_result, 0x04)

    def testReceiveSpuriousEmptyEvent(self):
        # check that we gracefully handle this weird case that
        # was causing Peephole to crash randomly after a while
        # of use.
        packet = []
        button_result = self.sendEvent(packet)
        self.failUnlessEqual(None, button_result)
