from chains.service import Service
from chains.common import log
import time, socket, subprocess

class LircService(Service):

    def onDescribe(self):
        return {
            'info': 'LIRC - Linux Infrared Remote Control',
            #'events': [
            #    ('IREvent', ('key','str',[]),('value','str',[]) )
            #],
        }

    def onInit(self):
        self.irsendBinary = self.config.get('irsend')
        self.lircSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.lircSocket.connect(self.config.get('socket'))
        self.interval = float(self.config.get('interval'))

    def onStart(self):
        while not self._shutdown:
            chunk = self.lircSocket.recv(512)
            if chunk:
                arr = chunk.split('\n')
                for i in arr:
                    i.replace('\n','')
                    if i:
                        raw, repeat, cmd, remote = i.split(' ')
                        self.sendEvent({
                            'device': remote,
                            'key': cmd,
                            'value': repeat,
                            'extra': {'raw': raw}
                        })
            time.sleep(self.interval)

    def action_irsend(self, remote, key, count=1):
        cmd = [
                self.irsendBinary, 
                'SEND_ONCE', 
                '--count=%s' % count, 
                remote, 
                key
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        ec = proc.wait()
        if ec != 0:
            raise Exception('Error (%s) when running: %s\nSTDOUT: %s\nSTDERR: %s' % (ret, cmd, out, err))

