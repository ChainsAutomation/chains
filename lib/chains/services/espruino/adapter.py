# apt-get install -y bluez libglib2.0-dev
# pip install bluepy

from __future__ import absolute_import
import time, datetime, re, copy, os
from bluepy import btle

class Config:
    def __init__(self):
        self.devices = []
    def addDevice(self, device):
        self.devices.append(device)
    def getDeviceByAddress(self, address):
        for device in self.devices:
            if device.address == address:
                return device

class ConfigDevice:
    def __init__(self, address, advertismentKeys, jsProgram, callback):
        self.address = address
        self.advertismentKeys = advertismentKeys
        self.jsProgram = jsProgram
        self.callback = callback

class ProgramFileReader:
    def __init__(self, file):
        if file[0] != '/':
            thisDir = os.path.dirname(os.path.realpath(__file__))
            file = '%s/%s' % (thisDir, file)
        self.file = file
    def read(self):
        fp = open(self.file, 'r')
        progData = fp.read()
        fp.close()
        return progData

class ScanDelegate(btle.DefaultDelegate):

    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self._lastAdvertising = {}
        self._lastState = {}
        self._config = None
        self._log = None

    def setConfig(self, config):
        self._config = config

    def setLog(self, log):
        self._log = log

    def handleDiscovery(self, dev, isNewDev, isNewData):

        configDevice = self._config.getDeviceByAddress(dev.addr)
        if not configDevice:
            return

        for (adtype, desc, value) in dev.getScanData():
            if adtype == 255 and value[:4] == "9005": # Manufacturer Data
                data = value[4:]
                if not dev.addr in self._lastAdvertising or self._lastAdvertising[dev.addr] != data:
                    state = self._splitAdvertismentData(data, configDevice.advertismentKeys)
                    self._log.info('ADV-DATA: %s => %s' % (dev.addr, state))
                    lastState = {}
                    if self._lastState.get(dev.addr):
                        lastState = self._lastState.get(dev.addr)
                    for key in state:
                        oldValue = lastState.get(key)
                        newValue = state[key]
                        if oldValue != newValue:
                            configDevice.callback(dev.addr, key, newValue)
                    self._lastState[dev.addr] = state
                self._lastAdvertising[dev.addr] = data

    def _splitAdvertismentData(self, data, keys):
        index = 0
        result = {}
        for key in keys:
            value = data[index:index+2]
            index += 2
            keyParts = key.split('.')
            _result = result
            if len(keyParts) > 1:
                for keyPartIndex in range(len(keyParts)-1):
                    keyPart = keyParts[keyPartIndex]
                    if not _result.has_key(keyPart):
                        _result[keyPart] = {}
                    _result = _result[keyPart]
            lastKey = keyParts.pop()
            _result[lastKey] = int(value, 16) # hex to dec
        return result


class Adapter:

    def __init__(self, config, log):

        # Init

        self.running = True
        self.scanning = False
        self.log = log
        self.log.info('Starting EspruinoService')

        # Set up scanning for advertisments

        delegate = ScanDelegate()
        delegate.setLog(log)
        delegate.setConfig(config)
        self.scanner = btle.Scanner().withDelegate(delegate)

        # Upload js program(s)

        self._btUpload(config)

        # Start scanning

        self.scanning = True
        self.scanner.clear()
        self.scanner.start(passive=True) # passive important for speed

    def _btUpload(self, config):
        for device in config.devices:
            self.log.info('upload js-program: %s' % (device.address))
            self._btSendProgram(device.address, device.jsProgram)
            self.log.info('uploaded js-program: %s' % (device.address))

    def _btConnect(self, address):
        self.log.info('btConnect start: %s' % address)
        tries = 0
        maxTries = 3
        while True:
            tries += 1
            if tries >= maxTries:
                self.log.info('btConnect given up after %s tries: %s' % (maxTries, address))
                return False
            try:
                peripheral = btle.Peripheral(address, "random")
                nus = peripheral.getServiceByUUID(btle.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E"))
                nustx = nus.getCharacteristics(btle.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"))[0]
                nusrx = nus.getCharacteristics(btle.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"))[0]
                nusrxnotifyhandle = nusrx.getHandle() + 1
                self.log.info('btConnect succeeded: %s' % (address))
                return (peripheral, nustx, nusrxnotifyhandle)

            except btle.BTLEDisconnectError:
                self.log.info('btConnect failed, will retry in 1: %s' % (address))
                time.sleep(1)

    def _btDisconnect(self, address, peripheral):
        self.log.info('btDisconnect: %s' % address)
        peripheral.disconnect()

    def _btSendProgram(self, address, commands):
        conn = self._btConnect(address)
        if conn == False:
            return
        (peripheral, nustx, nusrxnotifyhandle) = conn
        # Format
        command = '\x03'
        for c in commands.split("\n"):
            c = c.strip()
            if not c: continue
            command += '\x10' + c + '\n'
        peripheral.writeCharacteristic(nusrxnotifyhandle, b"\x01\x00", withResponse=False)
        # Send data (chunked to 20 bytes)
        while len(command)>0:
            nustx.write(command[0:20]);
            command = command[20:];
        self._btDisconnect(address, peripheral)

    def run(self):
        while self.running:
            """ no need for queue
            if len(self.programQueue) > 0:
                self.scanning = False
                self.scanner.stop()
                while len(self.programQueue) > 0:
                    prog = self.programQueue.pop(0)
                    self._btSendProgram(prog.address, prog.program)
                self.scanner.start(passive=True)
                self.scanning = True
            """
            if self.scanning:
                try:
                    self.scanner.process(10)
                except Exception, e:
                    if self.running:
                        self.log.error("Exception during process: %s" % (e))
                    else:
                        self.log.info("Ignore exception during process since shutting down: %s" % (e))
            else:
                time.sleep(0.2)
        if self.scanner:
            try:
                self.scanner.stop()
            except Exception, e:
                self.log.info("Ignore exception during scanner.stop since shutting down: %s" % (e))

    def stop(self):
        self.log.info('Stop called')
        self.running = False
        if self.scanning:
            self.log.info('Stop scanner')
            self.scanner.stop()
            self.scanning = False
        self.log.info('Stop finished')

    def sendProgram(self, addr, program):
        self.log.info('queueProgram: %s => %s' % (addr, program))
        #self.programQueue.append(QueuedProgram(addr, program))
        self._btSendProgram(addr, program)
