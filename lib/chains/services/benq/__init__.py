from __future__ import absolute_import
import time

from chains.service import Service
from chains.common import log
import serial
from . import benq


class BenqService(Service):

    def onInit(self):
        log('BenqService init.')
        self.model = self.config.get('model') or 'W6000'
        self.location = self.config.get('location')
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
        meta = {'type': 'screen', 'device': 'projector'}
        if self.location:
            meta.update({'location': self.location})
        while not self._shutdown:
            line = self.ser.readline()
            if line:
                change = benq.parse(line)
                self.sendEvent('change', change, meta)
            # TODO: sleep probably not needed?
            time.sleep(0.1)

    def _write_cmd(self, command):
        self.ser.write(command + '\r\n')
