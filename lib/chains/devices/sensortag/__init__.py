import sys
import time
import datetime

import chains.device
from chains.common import log

import pexpect

class SensorTagDevice(chains.device.Device):

    def onInit(self):
        log('SensorTag init')
        self.interval = self.config.getInt('interval') or 1000  # milliseconds


    def onStart(self):
        while not self._shutdown:
            sleep(self.interval / 1000)
