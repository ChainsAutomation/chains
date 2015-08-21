#!/usr/bin/python2

import sys
import time

from chains.service import Service
from chains.common import log
import serial
from . import cimage


class CImageService(Service):

    def onInit(self):
        log('CV image init.')

# TODO: Decide:
# * Pure action service, handling existing images?
# * Keep watching a cam for matching and such?

#    def onStart(self):
#        log('CV Image starting.')
#        while not self._shutdown:
#            # TODO: sleep probably not needed?
#            time.sleep(0.1)

