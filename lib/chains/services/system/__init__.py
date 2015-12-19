from chains.service import Service
from chains.common import log

from .system import System as SS

import os
import datetime
import time


class SystemService(Service):

    def onInit(self):
        self.interval = self.config.getInt('interval') or 60
        self.location = self.config.get('location')
        log.info('SystemService interval is: ')
        log.info(self.interval)

    def onStart(self):
        """ start loop """
        # let user defined how often to update data
        log.info('SystemService main loop starting')
        while not self._shutdown:
            log.info('Main loop running')
            self.action_sysinfo()
            self.action_meminfo()
            self.action_cpuinfo()
            self.action_userprocinfo()
            self.action_diskinfo()
            self.action_netinfo()
            # wait a while before sending system info again
            time.sleep(self.interval)

    def action_sysinfo(self):
        """ Get system information """
        sysinfo = SS.get_sysinfo()
        meta = {'device': 'system'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('system_update', sysinfo, meta)

    def action_meminfo(self):
        """ Get memory information """
        meminfo = SS.get_meminfo()
        meta = {'device': 'memory'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('memory_update', meminfo, meta)

    def action_cpuinfo(self):
        """ Get cpu information """
        cpuinfo = SS.get_cpuinfo()
        meta = {'device': 'cpu'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('cpu_update', cpuinfo, meta)

    def action_userprocinfo(self):
        """ Get user and process information """
        userproc = SS.get_userprocinfo()
        meta = {'device': 'userproc'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('userprocess_update', userproc, meta)

    def action_diskinfo(self):
        """ Get disk information """
        disk = SS.get_diskinfo()
        meta = {'device': 'disk'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('disk_update', disk, meta)

    def action_netinfo(self):
        """ Get network information """
        net = SS.get_netinfo()
        meta = {'device': 'network'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('network_update', net, meta)
