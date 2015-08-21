import sys
import time
import datetime

import chains.service
from chains.common import log

import pexpect

class SensorTagService(chains.service.Service):

    def onInit(self):
        log('SensorTag init')
        self.interval = self.config.getInt('interval') or 1000  # milliseconds


    def onStart(self):
        while not self._shutdown:
            sleep(self.interval / 1000)
