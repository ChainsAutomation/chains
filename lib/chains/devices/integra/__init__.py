#!/usr/bin/python2

import sys
import time

from chains.device import Device
from chains.common import log
import serial
from . import iscp


class IntegraDevice(Device):

    def onInit(self):
        log('IntegraDevice init.')
        self.model = self.config.get('model')
        self.ser_dev = self.config.get('serial')
        if self.ser_dev and self.model:
            self.cmds = iscp.model_cmds(self.model)
        else:
            log.error('Device needs serial device and model to work.')
            sys.exit(1)
        self.ser = serial.Serial(port=self.ser_dev,
                                 baudrate=9600,
                                 timeout=0,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 )

    def onStart(self):
        log('IntegraDevice starting.')
        while not self._shutdown:
            line = self.ser.readline()
            if line:
                self.sendEvent(line[1:4], {'value': line[4:]})
            time.sleep(0.1)

    def _write_cmd(self, topic, param):
        self.ser.write("!" + topic + param + '\r\n')

    # Start of runAction command, from Stians pastebin example
    def runAction(self, action, args):
        # chains-admin device action mydevid setVolume 50
        if action == 'setVolume':
            serial.send('VOL=%s' % args[0])
            return True
        # chains-admin device action mydevid getVolume
        elif action == 'getVolume':
            serial.send('VOL?')
            value = serial.recv()
            return int(value)
        # chains-admin device action mydevid reboot
        elif action == 'reboot':
            subprocess.call(['reboot'])
            return True
        elif action == 'describe':
            # TODO: Generate command array for specific device:
            return {
                'info': 'My amazing device',
                'actions': [
                    {
                        'name': 'setVolume',
                        'info': 'Set da volume woop woop',
                        'args': [
                            {'info': 'Volume value.', 'default': None, 'required': True, 'key': 'volume', 'type': 'int'}
                        ]
                    },
                    {
                        'name': 'getVolume',
                        'info': 'Get current volume',
                        'args': []
                    }
                ]
            }
        else:
            raise NoSuchActionException(action)
