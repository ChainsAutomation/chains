import psutil as ps
import platform as pf
import datetime
import os


class System(object):

    def get_sysinfo(self):
        """ Gather system info into a dictionary
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

    def get_meminfo(self):
        """ gather memory info into a dictionary """
        meminfo = {}
        if 'phymem_usage' in vars(ps):
            usage = ps.phymem_usage()
            meminfo.update({'mem_percent': ps.phymem_usage().percent})
            meminfo.update({'mem_free': self._try_get_mem_attr(usage, 'free')})
            meminfo.update({'mem_used': self._try_get_mem_attr(usage, 'used')})
            meminfo.update({'mem_available': self._try_get_mem_attr(usage, 'available')})
            meminfo.update({'mem_total': self._try_get_mem_attr(usage, 'total')})
            meminfo.update({'mem_active': self._try_get_mem_attr(usage, 'active')})
            meminfo.update({'mem_buffer': self._try_get_mem_attr(usage, 'buffers')})
            meminfo.update({'mem_cached': self._try_get_mem_attr(usage, 'cached')})
            meminfo.update({'mem_inactive': self._try_get_mem_attr(usage, 'inactive')})
        return meminfo

    def get_cpuinfo(self):
        """ gather cpu info into a dictionary """
        cpu = ps.cpu_times()
        cpuinfo = {
            'percent':    ps.cpu_percent(),  # set interval=1?0.5?
            'user':       self._try_get_attr(cpu, 'user'),
            'nice':       self._try_get_attr(cpu, 'nice'),
            'system':     self._try_get_attr(cpu, 'system'),
            'idle':       self._try_get_attr(cpu, 'idle'),
            'iowait':     self._try_get_attr(cpu, 'iowait'),
            'irq':        self._try_get_attr(cpu, 'irq'),
            'softirq':    self._try_get_attr(cpu, 'softirq'),
            'guest':      self._try_get_attr(cpu, 'guest'),
            'guest_nice': self._try_get_attr(cpu, 'guest_nice'),
            'steal':      self._try_get_attr(cpu, 'steal'),
        }
        return cpuinfo

    def get_userprocinfo(self):
        """ gather process info into a dictionary """
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

    def get_diskinfo(self):
        """ gather disk info into a dictionary """
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

    def get_netinfo(self):
        """ gather neetwork info into a dictionary """
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

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    mys = System()
    print "Sys info:"
    print mys.get_sysinfo()
    print "Mem info:"
    print mys.get_meminfo()
    print "CPU info:"
    print mys.get_cpuinfo()
    print "User-Process info:"
    print mys.get_userprocinfo()
    print "Disk info:"
    print mys.get_diskinfo()
    print "Netinfo:"
    print mys.get_netinfo()

