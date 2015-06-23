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
            self.topics, self.cmds = iscp.model_cmds(self.model)
        else:
            log.error('Device needs serial device and model to work.')
            sys.exit(1)
        self.ser = serial.Serial(port=self.ser_dev,
                                 baudrate=9600,
                                 timeout=0.05,  # 50ms reponse time according to spec
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
        self.ser.write("!1" + topic + param + '\r\n')

    # Start of runAction command, from Stians pastebin example
    def runAction(self, action, args):
        if action[:3] in self.topics:
        command = False
            if action[3:] in self.cmds[action[:3]]:
                if not self.cmds[action[:3]][action[3:]]['type']
                    command = action
                else:
                    command = iscp.check_cmd(action[:3], args[0], self.cmds[action[:3]][action[3:]]['type'])
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
        if not command:
            raise NoSuchActionException(action)
        self._write_cmd(command)

