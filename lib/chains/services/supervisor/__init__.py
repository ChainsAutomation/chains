#!/usr/bin/python

import time
from chains.service import Service
from chains.common import log
import supervisor.xmlrpc
import xmlrpclib
from . import supervisor as sprv


class SupervisorService(Service):

    def onInit(self):
        log('Starting Supervisor service')
        self.interval = self.config.getInt('interval') or 300  # seconds
        self.server = xmlrpclib.ServerProxy(
            'http://127.0.0.1',
            transport=supervisor.xmlrpc.SupervisorTransport(
                None, None,
                'unix:///var/run/supervisor.sock'
            )
        )

    def onStart(self):
        while not self._shutdown:
            cur_state = self._get_state()
            self._send_server_state()
            self._send_state(cur_state)
            time.sleep(self.interval)

    def _send_state(self, progs):
        for program in progs:
            self.sendEvent(program, progs[program])

    def _send_server_state(self):
        srv_state = self._get_server_state(self.server)
        if srv_state:
            self.sendEvent('server_state', {'value': srv_state['statename']})
        else:
            self.sendEvent('error', {'type': 'server_state', 'program': 'supervisor'})

    def _get_state(self):
        # Fetch current state from supervisor
        return sprv.state(self.server)

    def _get_server_state(self):
        # Fetch current server state from supervisor
        return sprv.server_state(self.server)

    def action_server_state(self):
        '''
        Get supervisor server state
        '''
        srv_state = self._get_server_state(self.server)
        if srv_state:
            self.sendEvent('server_state', {'value': srv_state['statename']})
        else:
            self.sendEvent('error', {'type': 'server_state', 'program': 'supervisor'})


    def action_server_shutdown(self):
        '''
        Get shutdown supervisor server
        '''
        if sprv.server_shutdown(self.server):
            self.sendEvent('server_state', {'value': 'SHUTDOWN'})
        else:
            self.sendEvent('error', {'type': 'server_shutdown', 'program': 'supervisor'})

    def action_server_restart(self):
        '''
        Get restart supervisor server
        '''
        if sprv.server_restart(self.server):
            self.sendEvent('server_state', {'value': 'RESTARTING'})
        else:
            self.sendEvent('error', {'type': 'server_restart', 'program': 'supervisor'})

    def action_program_info(self, program):
        '''
        Get program info
        @param  program     string   Program name
        '''
        info = sprv.info(self.server, program)
        if info:
            self.sendEvent(program, info)
        else:
            self.sendEvent('error', {'type': 'info', 'program': program})

    def action_start(self, program):
        '''
        Start program
        @param  program     string   Program name
        '''
        start = sprv.start(self.server, program)
        if start:
            self.sendEvent('start', {'value': program})
        else:
            self.sendEvent('error', {'type': 'start', 'program': program})

    def action_start_all(self):
        '''
        Start all programs
        '''
        if sprv.start_all(self.server):
            self.sendEvent('start_all', {'program': 'supervisor'})
        else:
            self.sendEvent('error', {'type': 'start_all', 'program': 'supervisor'})

    def action_start_group(self, group):
        '''
        Start group
        @param  group     string   Group name
        '''
        start = sprv.start_group(self.server, group)
        if start:
            self.sendEvent('start_group', {'value': group})
        else:
            self.sendEvent('error', {'type': 'start_group', 'group': group})

    def action_stop(self, program):
        '''
        Stop program
        @param  program     string   Program name
        '''
        stop = sprv.stop(self.server, program)
        if stop:
            self.sendEvent('stop', {'value': program})
        else:
            self.sendEvent('error', {'type': 'stop', 'program': program})

    def action_stop_all(self):
        '''
        Stop all programs
        '''
        stop = sprv.stop_all(self.server)
        if stop:
            self.sendEvent('stop_all', {'program': 'supervisor'})
        else:
            self.sendEvent('error', {'type': 'stop_all', 'program': 'supervisor'})

    def action_stop_group(self, group):
        '''
        Stop group
        @param  group     string   Group name
        '''
        stop = sprv.stop_group(self.server, group)
        if stop:
            self.sendEvent('stop_group', {'value': group})
        else:
            self.sendEvent('error', {'type': 'stop_group', 'group': group})

    def action_restart(self, program):
        '''
        Restart program
        @param  program     string   Program name
        '''
        restart = sprv.restart(self.server, program)
        if restart:
            self.sendEvent('restart', {'program': program})
        else:
            self.sendEvent('error', {'type': 'restart', 'program': program})

    def action_restart_group(self, group):
        '''
        Restart group
        @param  group     string   Group name
        '''
        restart = sprv.restart_group(self.server, group)
        if restart:
            self.sendEvent('restart', {'group': group})
        else:
            self.sendEvent('error', {'type': 'restart', 'group': group})

    def action_state(self):
        '''
        Get all program state
        '''
        cur_state = self._get_state()
        self._send_state(cur_state)
