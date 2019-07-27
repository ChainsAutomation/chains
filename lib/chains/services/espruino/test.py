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

def sendEvent(key, data, devAttr):
    log.info('sendEvent: key=%s, data=%s, devAddr=%s' % (key, data, devAttr))

def callback(addr, key, values):
    log.info('btEventCallback: %s = %s' % (key, values))

    device = key
    deviceAttributes = {}

    # todo: lookup device name from address
    #deviceAttributes['device'] = device
    deviceAttributes['device'] = device # now battery, temperature, etc

    data = {}
    for valueKey in values:
        valueValue = values[valueKey]
        data[valueKey] = {"value": valueValue}
    #log.info('sendEvent: data=%s attr=%s' % (data, deviceAttributes))

    sendEvent('change', data, deviceAttributes)

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
