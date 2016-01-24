#!/usr/bin/python2

import sys
import time

from chains.service import Service, NoSuchActionException
from chains.common import log
import serial
from . import iscp


class IntegraService(Service):

    def onInit(self):
        log.info('IntegraService init.')
        self.model = self.config.get('model')
        self.ser_dev = self.config.get('serial')
        if self.ser_dev and self.model:
            self.topics, self.cmds = iscp.model_cmds(self.model)
        else:
            log.error('Service needs serial service and model to work.')
            sys.exit(1)
        self.act_desc = {
            'info': 'Integra/Onkyo model %s' % self.model,
            'actions': []
        }
        for cmd in self.cmds:
            for subcmd in self.cmds[cmd]:
                newcmd = {
                    'name': cmd + subcmd,
                    'info': self.cmds[cmd][subcmd]['description'],
                    'args': [
                    ]
                }
                # matches non-empty type-dicts:
                if self.cmds[cmd][subcmd]['type']:
                    param = self._type_desc(self.cmds[cmd][subcmd]['type'])
                    if param:
                        newcmd['args'].append(param)
                self.act_desc['actions'].append(newcmd)
        self.ser = serial.Serial(port=self.ser_dev,
                                 baudrate=9600,
                                 timeout=0.05,  # 50ms reponse time according to spec
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 )

    def onStart(self):
        log.info('IntegraService starting.')
        while not self._shutdown:
            # TODO: check for self.command variable, and run command here
            # rather than from runAction()?
            line = self.ser.readline()
            if line:
                self.sendEvent(line[1:4], {'value': line[4:]})
            # TODO: sleep probably not needed?
            time.sleep(0.1)

    def _write_cmd(self, command):
        self.ser.write("!1" + command + '\r\n')

    def _type_desc(self, tdesc):
        # Create dict like this:
        # {'info': 'Volume value.', 'default': None, 'required': True, 'key': 'volume', 'type': 'int'}
        # TODO: Figure out info, get from main cmd?
        arg_dict = {'info': '', 'default': None, 'required': True}
        if tdesc['type'] == 'noarg':
            return None
        elif tdesc['type'] == 'string':
            arg_dict.update({'type': 'string'})
        elif tdesc['type'] == 'range':
            arg_dict.update({'type': 'int(min=%d, max=%d)' % (tdesc['min'], tdesc['max'])})
        else:
            return None
        return arg_dict

    # Start of runAction command, from Stians pastebin example
    def runAction(self, action, args):
        if action[:3] in self.topics:
            if action[3:] in self.cmds[action[:3]]:
                if not self.cmds[action[:3]][action[3:]]['type']:
                    command = action
                else:
                    # At this point we know that action[3:] is a placeholder for args[0]
                    # Since no commands take more than one arg, always args[0]
                    command = iscp.check_cmd(action[:3], args[0], self.cmds[action[:3]][action[3:]]['type'])
        elif action == 'raw':
            command = self._write_cmd(args[0])
        # TODO: this?
        # elif action == 'multi':
        #     for arg in args:
        #         # do something with each arg
        #         pass
        elif action == 'describe':
            return self.act_desc
        else:
            raise NoSuchActionException(action)
        if not command:
            raise NoSuchActionException(action)
        self._write_cmd(command)
