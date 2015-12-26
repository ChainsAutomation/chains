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
        self.cs = SS()
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
        sysinfo = self.cs.get_sysinfo()
        sysinfo = self.cdictify(sysinfo)
        meta = {'device': 'system'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('system_update', sysinfo, meta)

    def action_meminfo(self):
        """ Get memory information """
        meminfo = self.cs.get_meminfo()
        meminfo = self.cdictify(meminfo)
        meta = {'device': 'memory'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('memory_update', meminfo, meta)

    def action_cpuinfo(self):
        """ Get cpu information """
        cpuinfo = self.cs.get_cpuinfo()
        cpuinfo = self.cdictify(cpuinfo)
        meta = {'device': 'cpu'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('cpu_update', cpuinfo, meta)

    def action_userprocinfo(self):
        """ Get user and process information """
        userproc = self.cs.get_userprocinfo()
        userproc = self.cdictify(userproc)
        meta = {'device': 'userproc'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('userprocess_update', userproc, meta)

    def action_diskinfo(self):
        """ Get disk information """
        disk = self.cs.get_diskinfo()
        disk = self.cdictify(disk)
        meta = {'device': 'disk'}
        if self.location:
            meta.update({'location': self.location})
        self.sendEvent('disk_update', disk, meta)

    def action_netinfo(self):
        """ Get network information """
        net = self.cs.get_netinfo()
        for neti in net:
            meta = {'device': 'net-%s' % neti}
            ndict = self.cdictify(net[neti])
            if self.location:
                meta.update({'location': self.location})
            self.sendEvent('network_update', ndict, meta)

    def cdictify(self, flat_dict):
        cdict = {}
        for key, value in flat_dict.items():
            cdict.update({key: {'value': value}})
        return cdict
