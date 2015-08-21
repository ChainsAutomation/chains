#!/usr/bin/python2

import sys
import time

from chains.service import Service
from chains.common import log
import serial
from . import benq


class BenqService(Service):

    def onInit(self):
        log('BenqService init.')
        self.model = self.config.get('model') or 'W6000'
        self.ser_dev = self.config.get('serial') or '/dev/ttyUSB0'
        self.ser = serial.Serial(port=self.ser_dev,
                                 baudrate=115200,
                                 timeout=0.05,  # TODO: What is spec?
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 )

    def onStart(self):
        log('BenqService starting.')
        while not self._shutdown:
            line = self.ser.readline()
            if line:
                self.sendEvent(line, {'value': line})
            # TODO: sleep probably not needed?
            time.sleep(0.1)

    def _write_cmd(self, command):
        self.ser.write(command + '\r\n')
