# apt-get install -y bluez libglib2.0-dev
# pip install bluepy

from __future__ import absolute_import
from bluepy import btle
import time, datetime, re, copy, os
import time
import chains.service
from chains.common import log

"""
class Log:
    def info(self, msg):
        self._log(msg)
    def warn(self, msg):
        self._log(msg)
    def _log(self, msg):
        print 'LOG: %s' % msg
log = Log()
"""

"""
# Receiver for notifications on this side
class NUSRXDelegate(btle.DefaultDelegate):
    def __init__(self):
        self.chainsService = None
        btle.DefaultDelegate.__init__(self)
        self.buffer = ''
        # ... initialise here
    def handleNotification(self, cHandle, data):
        log.info('EspruinoService.NUSRXDelegate.RX: %s' % (data,))
        try:
            pat = re.compile('#st#([^#]+)#/st#')
            self.buffer += data
            mat = None
            for mat in pat.finditer(self.buffer):
                data = mat.group(1)
                #log.info('DATA: %s' % data)
                keyval = data.split(';')
                key = keyval.pop(0)
                type = keyval.pop(0)
                val = ';'.join(keyval)
                self.chainsService.sendEventWrapper(key, type, val)
            if mat:
                #log.info('LEN: %s END: %s' % (len(self.buffer), mat.end()))
                self.buffer = self.buffer[mat.end():]
                #log.info('REST: %s' % self.buffer)
        except Exception, e:
            log.info('EspruinoService.NUSRXDelegate.ERR: error handling last message: %s' % (e,))
    def setChainsService(self, service):
        self.chainsService = service
"""

class ScanDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self._lastAdvertising = {}
        self._lastState = {}
    def setAddresses(self, addresses):
        self.addresses = addresses
    def setChainsDevice(self, device):
        self.chainsDevice = device
    def _splitAdvertismentData(self, data):
        keys = ['button','battery','temperature','light']
        index = 0
        result = {}
        #print 'DATA: %s' % data
        for key in keys:
            value = data[index:index+2]
            index += 2
            result[key] = int(value, 16) # hex to dec
        return result
    def handleDiscovery(self, dev, isNewDev, isNewData):
        if not dev.addr in self.addresses:
            return
        #print 'DISCO: %s' % dev.addr
        for (adtype, desc, value) in dev.getScanData():
            #print '- DATA: %s : %s : %s' % (adtype, desc, value)
            if adtype==255 and value[:4]=="9005": # Manufacturer Data
                #print 'DATA: %s' % (value)
                data = value[4:]
                if not dev.addr in self._lastAdvertising or self._lastAdvertising[dev.addr] != data:
                    #onDeviceChanged(dev.addr, data)
                    state = self._splitAdvertismentData(data)
                    log.info('ADV-DATA: %s' % state)
                    for key in state:
                        oldValue = self._lastState.get(key)
                        newValue = state[key]
                        if oldValue != newValue:
                            self.chainsDevice.sendEventWrapper(key, newValue)
                self._lastAdvertising[dev.addr] = data


class EspruinoService(chains.service.Service):
#class DummyEspruinoService():

    def onInit(self):

        #self.config = {"address": "e0:be:3a:91:85:b5"} # tmp
        log.info('Starting EspruinoService')
        self.address = self.config.get('address') # NRF.getAddress() on Puck console
        log.info('address = %s' % self.address)

        self.running = True

        delegate = ScanDelegate()
        delegate.setAddresses([self.address])
        delegate.setChainsDevice(self)
        self.scanning = False
        self.scanner = btle.Scanner().withDelegate(delegate)
        self.programQueue = []

        self.btUpload()

        self.scanning = True
        self.scanner.clear()
        self.scanner.start(passive=True) # passive important for speed

    def btConnect(self):
        log.info('btConnect start')
        tries = 0
        maxTries = 3
        while True:
            tries += 1
            if tries >= maxTries:
                log.info('btConnect given up after %s tries' % maxTries)
                return False
            try:
                self.peripheral = btle.Peripheral(self.address, "random")
                nus = self.peripheral.getServiceByUUID(btle.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E"))
                self.nustx = nus.getCharacteristics(btle.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"))[0]
                self.nusrx = nus.getCharacteristics(btle.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"))[0]
                self.nusrxnotifyhandle = self.nusrx.getHandle() + 1
                """
                d = NUSRXDelegate()
                d.setChainsService(self)
                self.peripheral.setDelegate(d)
                """

                log.info('btConnect succeeded')
                return True

            except btle.BTLEDisconnectError:
                log.info('btConnect failed, will retry in 1')
                time.sleep(1)

    def btDisconnect(self):
        log.info('btDisconnect start')
        self.peripheral.disconnect()
        self.nustx = None
        self.nusrx = None
        self.nusrxnotifyhandle = None
        log.info('btDisconnect done')

    def btUpload(self):

        # Initial program
        # @todo: relative path
        thisDir = os.path.dirname(os.path.realpath(__file__))
        progFile = '%s/program.js' % thisDir
        fp = open(progFile, 'r')
        progData = fp.read()
        fp.close()
        log.info('read initial program')
        self.sendProgram(progData)
        log.info('sent initial program')

    def onStart(self):
        # Keep scanning in  10 second chunks
        while self.running:
            """
            print ''
            print '=' * 50
            print 'scan'
            print '=' * 50
            print ''
            """
            if self.scanning:
                self.scanner.process(10)
            else:
                time.sleep(0.2)
        # in case were wanted to finish, we should call 'stop'
        scanner.stop()
        """
        while True:
            try:
                self.peripheral.waitForNotifications(1.0)
                while len(self.programQueue) > 0:
                    prog = self.programQueue.pop(0)
                    log.info('send prog: %s' % prog)
                    self.sendProgram(prog)
            except btle.BTLEDisconnectError:
                log.info('BT disconnect, will reconnect in 1')
                time.sleep(1)
                self.btConnect()
        """

    def onShutdown(self):
        self.running = False
        if self.scanning:
            self.scanner.stop()
            self.scanning = False
        self.peripheral.disconnect()


    def queueProgram(self, commands):
        log.info('queue prog: %s' % commands)
        self.programQueue.append(commands)

    # re-program puck.js
    def sendProgram(self, commands):
        wasScanning = False
        if self.scanning:
            wasScanning = True
            self.scanning = False
            self.scanner.stop()
        if self.btConnect():
            # Format
            command = '\x03'
            for c in commands.split("\n"):
                c = c.strip()
                if not c: continue
                command += '\x10' + c + '\n'
            #log.info('sendProgram: %s' % command)
            #print command
            # Start
            #self.peripheral.writeCharacteristic(self.nusrxnotifyhandle, b"\x01\x00", withResponse=True)
            self.peripheral.writeCharacteristic(self.nusrxnotifyhandle, b"\x01\x00", withResponse=False)
            # Send data (chunked to 20 bytes)
            while len(command)>0:
                self.nustx.write(command[0:20]);
                command = command[20:];
            self.btDisconnect()
        if wasScanning:
            self.scanning = True
            self.scanner.start()

    def action_reset(self):
        self.sendProgram('reset();')

    def action_blink(self, index, toggle):
        index = int(index)
        if index != 1 and index != 2:
            raise Exception('Only index 1 and 2 supported')
        toggleString = 'false'
        if toggle:
            toggleString = 'true'
        self.queueProgram('setBlink(%s, %s);' % (index, toggleString))

    def sendEventWrapper(self, key, value):
        log.info('sendEvent: %s = %s' % (key,value))

        device = key
        deviceAttributes = {}
        deviceAttributes['device'] = device
        data = {}
        data[key] = {"value": value}
        log.info('sendEventWrapper: data=%s attr=%s' % (data, deviceAttributes))

        self.sendEvent('change', data, deviceAttributes)


"""
if __name__ == '__main__':
    d = DummyEspruinoService()
    d.onInit()
    d.onStart()
"""
