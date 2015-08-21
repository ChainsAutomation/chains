#!/usr/bin/python2

import sys
import time

from chains.service import Service
from chains.common import log
import serial
from . import usbhub


class USBHubService(Service):

    def onInit(self):
        log('USBHub init.')
        self.interval = self.config.get('interval') or 60

    def onStart(self):
        log('USBHub starting.')
        while not self._shutdown:
            # TODO: send port status every <interval> seconds
            time.sleep(self.interval)

    # TODO: Stub
    def action_hub_power_off(self, bus, address):
        pass

    # TODO: Stub
    def action_hub_power_on(self, bus, address):
        pass

    # TODO: Stub
    def action_hub_power_toggle(self, bus, address):
        pass

    # TODO: Stub
    def action_port_power_off(self, bus, address, port):
        pass

    # TODO: Stub
    def action_port_power_on(self, bus, address, port):
        pass

    # TODO: Stub
    def action_port_power_toggle(self, bus, address, port):
        pass


    # TODO: Stub
    def action_led_toggle(self, bus, address, port):
        pass

    # TODO: Stub
    def action_led_on(self, bus, address, port):
        pass

    # TODO: Stub
    def action_led_off(self, bus, address, port):
        pass

    # TODO: Stub
    def action_all_hub_status(self):
        pass

    # TODO: Stub
    def action_hub_status(self, bus, address):
        pass

    # TODO: Stub
    def action_port_status(self, bus, address, port):
        pass

