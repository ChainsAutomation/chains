from chains.device import Device
from chains.common import log

import os
import datetime
import time
import psutil as ps
import platform as pf

class SystemDevice(Device):

    def onInit(self):
        self.interval = self.config.getInt('interval') or 60
        log.info('SystemDevice interval is: ')
        log.info(self.interval)

    def onStart(self):
        """ start loop """
        # let user defined how often to update data
        log.info('SystemDevice main loop starting')
        while not self._shutdown:
            log.info('Main loop running')
            self.action_cpuinfo()
            self.action_meminfo()
            self.action_netinfo()
            self.action_sysinfo()
            self.action_diskinfo()
            # wait a while before sending system info again
            time.sleep(self.interval)

    def action_sysinfo(self):
        """ Get system information """
        sysinfo = self._get_sysinfo()
        self.sendEvent('system', sysinfo)

    def action_meminfo(self):
        """ Get memory information """
        meminfo = self._get_meminfo()
        self.sendEvent('memory', meminfo)

    def action_cpuinfo(self):
        """ Get cpu information """
        cpuinfo = self._get_cpuinfo()
        self.sendEvent('cpu', cpuinfo)

    def action_userprocinfo(self):
        """ Get user and process information """
        userproc = self._get_userprocinfo()
        self.sendEvent('userprocess', userproc)

    def action_diskinfo(self):
        """ Get disk information """
        disk = self._get_diskinfo()
        self.sendEvent('disk', disk)

    def action_netinfo(self):
        """ Get network information """
        net = self._get_netinfo()
        self.sendEvent('network', net)

    def _get_sysinfo(self):
        """ Gather system info into a dictionary for sendEvent.
            This is information that rarely if ever changes. Well, yeah, this changed with the uptime stats.
        """
        sysinfo = {
            'hostname': os.uname()[1],
            'cpus': ps.cpu_count(logical=False),
            'cpu_cores': ps.cpu_count(),
            'architecture': pf.architecture()[0],
            'bin_format': pf.architecture()[1],
            'up_since': datetime.datetime.fromtimestamp(ps.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            'uptime': int((datetime.datetime.now() - datetime.datetime.fromtimestamp(ps.boot_time())).total_seconds() / 60),
        }
        return sysinfo

    def _get_meminfo(self):
        """ gather memory info into a dictionary for sendEvent """
        usage = ps.phymem_usage()
        meminfo = {
            'mem_percent': ps.phymem_usage().percent,
            'mem_free': self._try_get_mem_attr(usage, 'free'),
            'mem_used': self._try_get_mem_attr(usage, 'used'),
            'mem_available': self._try_get_mem_attr(usage, 'available'),
            'mem_total': self._try_get_mem_attr(usage, 'total'),
            'mem_active': self._try_get_mem_attr(usage, 'active'),
            'mem_buffer': self._try_get_mem_attr(usage, 'buffers'),
            'mem_cached': self._try_get_mem_attr(usage, 'cached'),
            'mem_inactive': self._try_get_mem_attr(usage, 'inactive'),
        }
        return meminfo

    def _get_cpuinfo(self):
        """ gather cpu info into a dictionary for sendEvent """
        cpu = ps.cpu_times()
        cpuinfo = {
            'cpu_percent':    ps.cpu_percent(),  # set interval=1?0.5?
            'cpu_user':       self._try_get_attr(cpu, 'user'),
            'cpu_nice':       self._try_get_attr(cpu, 'nice'),
            'cpu_system':     self._try_get_attr(cpu, 'system'),
            'cpu_idle':       self._try_get_attr(cpu, 'idle'),
            'cpu_iowait':     self._try_get_attr(cpu, 'iowait'),
            'cpu_irq':        self._try_get_attr(cpu, 'irq'),
            'cpu_softirq':    self._try_get_attr(cpu, 'softirq'),
            'cpu_guest':      self._try_get_attr(cpu, 'guest'),
            'cpu_guest_nice': self._try_get_attr(cpu, 'guest_nice'),
            'cpu_steal':      self._try_get_attr(cpu, 'steal'),
        }
        return cpuinfo

    def _get_userprocinfo(self):
        """ gather process info into a dictionary for sendEvent """
        terms = {}
        logins = {}
        for user in ps.users():
            terms.update({user.terminal: {'user': user.name, 'host': user.host, 'time': int((datetime.datetime.now() - datetime.datetime.fromtimestamp(user.started)).total_seconds() / 60)}})
            if user.name not in logins:
                logins.update({user.name: True})
        userprocinfo = {
            'pids': len(ps.pids()),
        }
        userprocinfo.update(terms)
        userprocinfo.update(logins)
        return userprocinfo

    def _get_diskinfo(self):
        """ gather disk info into a dictionary for sendEvent """
        mounts = {}
        for m in ps.disk_partitions():
            mounts.update({m.mountpoint: ps.disk_usage(m.mountpoint).percent})
        diskinfo = {
            'read_count': ps.disk_io_counters(perdisk=False).read_count,
            'write_count': ps.disk_io_counters(perdisk=False).write_count,
            'read_bytes': ps.disk_io_counters(perdisk=False).read_bytes,
            'write_bytes': ps.disk_io_counters(perdisk=False).write_bytes,
            'read_time': ps.disk_io_counters(perdisk=False).read_time,
            'write_time': ps.disk_io_counters(perdisk=False).write_time,
            # '': ,
        }
        diskinfo.update(mounts)
        return diskinfo

    def _get_netinfo(self):
        """ gather neetwork info into a dictionary for sendEvent """
        nics = {}
        try:
            niclist = ps.net_io_counters(pernic=True)
        except AttrbuteError:
            niclist = ps.network_io_counters(pernic=True)
        for nic in niclist:
            nics.update({nic: {}})
            for name in niclist[nic]._fields:
                nics[nic].update({name: getattr(niclist[nic], name)})
        return nics

    def _try_get_attr(self, obj, attr):
        try:
            return getattr(obj, attr)
        except AttributeError:
            return None

    def _try_get_mem_attr(self, obj, attr):
        value = None
        try:
            value = getattr(obj, attr)
        except AttributeError:
            return None
        return int(value / (1024 * 1024))
