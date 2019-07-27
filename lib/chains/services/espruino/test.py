import threading
import adapter
import time

class Log:
    def info(self, msg):
        self._log(msg)
    def warn(self, msg):
        self._log(msg)
    def error(self, msg):
        self._log(msg)
    def _log(self, msg):
        print 'LOG: %s' % msg
log = Log()

def callback(addr, key, value):
    print 'CALLBACK: %s : %s => %s' % (addr, key, value)

addr = 'e0:be:3a:91:85:b5'

c = adapter.Config()
c.addDevice(adapter.ConfigDevice(
    address=addr,
    advertismentKeys=['button.buttonCount','button.buttonLength', 'battery.battery','temperature.temperature','light.light'],
    jsProgram=adapter.ProgramFileReader('program.js').read(),
    callback=callback
))
a = adapter.Adapter(c, log)

class StartThread (threading.Thread):
    def __init__(self, a):
        threading.Thread.__init__(self)
        self.adapter = a
    def run(self):
        self.adapter.run()
    def shutdown(self):
        self.adapter.stop()

t = StartThread(a)
t.start()

try:
    while True:
        print 'TICK START'
        time.sleep(5)
        a.sendProgram(addr, "digitalPulse(LED2, 1, 100);")
        print 'TICK END'
except KeyboardInterrupt:
    print 'Shutting down'
    t.shutdown()
    t.join()
    print 'Exit'
