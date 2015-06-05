#!/usr/bin/python

import sys
import time
from chains.device import Device
from chains.common import log
import supervisor.xmlrpc
import xmlrpclib
from . import supervisor as sprv


class SupervisorDevice(Device):

    def onInit(self):
        self.interval = self.config.getInt('interval') or 300  # seconds
        self.server = xmlrpclib.ServerProxy(
            'http://127.0.0.1',
            transport=supervisor.xmlrpc.SupervisorTransport(
                None, None,
                'unix:///var/run/supervisor.sock'
            )
        )
        print self.server.supervisor.getState()

    def onStart(self):
        while not self._shutdown:
            cur_state = self._get_state()
            self._send_state(cur_state)
            time.sleep(self.interval)

    def _send_state(self, progs):
        for program in progs:
            self.sendEvent(program,
                           {
                               'key': 'val',
                           })

    def _get_state(self):
        # Fetch current state from supervisor
        pass

    def _get_server_state(self):
        # Fetch current server state from supervisor
        pass

    def action_stop(self, program):
        pass

    def action_stop_all(self, program):
        pass

    def action_stop_group(self, group):
        pass

    def action_start(self, program):
        pass

    def action_start_all(self, program):
        pass

    def action_start_group(self, group):
        pass

    def action_restart(self, program):
        pass

    def action_restart_group(self, group):
        pass

    def action_state(self, program):
        pass
