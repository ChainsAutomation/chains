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
            self.send_sysinfo()
            self.send_meminfo()
            self.send_cpuinfo()
            self.send_userprocinfo()
            self.send_diskinfo()
            self.send_netinfo()
            # wait a while before sending system info again
            time.sleep(self.interval)

    def send_sysinfo(self):
        """ Get system information """
        sysinfo = SS.get_sysinfo()
        meta = {'device': 'system'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('system_update', sysinfo, meta)

    # aliases for chains actions
    action_sysinfo = send_sysinfo

    def send_meminfo(self):
        """ Get memory information """
        meminfo = SS.get_meminfo()
        meta = {'device': 'memory'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('memory_update', meminfo, meta)

    # aliases for chains actions
    action_meminfo = send_meminfo

    def send_cpuinfo(self):
        """ Get cpu information """
        cpuinfo = SS.get_cpuinfo()
        meta = {'device': 'cpu'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('cpu_update', cpuinfo, meta)

    # aliases for chains actions
    action_cpuinfo = send_cpuinfo

    def send_userprocinfo(self):
        """ Get user and process information """
        userproc = SS.get_userprocinfo()
        meta = {'device': 'userproc'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('userprocess_update', userproc, meta)

    # aliases for chains actions
    action_userprocinfo = send_userprocinfo

    def send_diskinfo(self):
        """ Get disk information """
        disk = SS.get_diskinfo()
        meta = {'device': 'disk'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('disk_update', disk, meta)

    # aliases for chains actions
    action_diskinfo = send_diskinfo

    def send_netinfo(self):
        """ Get network information """
        net = SS.get_netinfo()
        meta = {'device': 'network'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('network_update', net, meta)

    # aliases for chains actions
    action_netinfo = send_netinfo
