from chains.service import Service
from chains.common import log
import subprocess, time

class PingService(Service):

    def onInit(self):
        self.down = {}
        self.interval = self.config.getInt('interval')
        self.timeout = self.config.getInt('timeout')
        self.count = self.config.getInt('count')
        self.hosts = self.config.data('pinghosts')
        self.pingBinary = self.config.get('pingbin')

    def onStart(self):
        if not self.hosts:
            log.warn('No hosts to ping')
            return
        started = False
        while not self._shutdown:
            for name in self.hosts:
                host = self.hosts[name]
                if self.ping(host):
                    if self.isDown(host) or not started:
                        self.sendEvent(name, {
                            'value': 'up',
                            'address': host
                        })
                        try: del self.down[host]
                        except: pass
                else:
                    if not self.isDown(host):
                        self.sendEvent(name, {
                            'value': 'down',
                            'address': host
                        })
                        self.down[host] = True
            started = True
            time.sleep(self.interval)

    def isDown(self, host):
        try:
            self.down[host]
            return True
        except KeyError:
            return False

    def ping(self, host):
        cmd = [self.pingBinary, '-c', '%s' % self.count, '-w', '%s' % self.timeout, '-n', host]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        ec = proc.wait()
        if ec == 0:
            log.debug('ping up (%s): %s : %s' % (ec, host, cmd))
            return True
        else:
            log.debug('ping down (%s): %s : %s' % (ec, host, cmd))
            return False
        
    def action_ping(self, host):
        '''
        Ping a host
        @param host string The host to ping
        '''
        return self.ping(host)

    def onDescribe(self):
        return {
            'info': 'Pings hosts and sends up/down events',
            'events': [
                {
                    'id': 'state',
                    'key': {
                        'info': 'Name of host that is up or down (key part of line in service config)'
                    },
                    'data': {
                        'value': {
                            'type': 'string', 
                            'valid': ['up','down'],
                            'info': 'Up if replies to ping'
                        },
                        'address': {
                            'type': 'string',
                            'info': 'IP or hostname as configured in config (value part of line in service config)'
                        },
                    },
                    'info': 'Event that signals that a host changed to up or down'
                }
            ],
        }

