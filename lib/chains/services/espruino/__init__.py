# apt-get install -y bluez libglib2.0-dev
# pip install bluepy

from __future__ import absolute_import
from bluepy import btle
import chains.service
from chains.common import log
import time, datetime, re, copy
import time

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

class EspruinoService(chains.service.Service):
#class DummyEspruinoService():

    def onInit(self):

        self.programQueue = []

        #self.config = {"puckaddress": "e0:be:3a:91:85:b5"} # tmp

        log.info('Starting EspruinoService')
        self.address = self.config.get('address') # NRF.getAddress() on Puck console
        log.info('address = %s' % self.address)

        self.btConnect()
        self.btUpload()

    def btConnect(self):

        while True:

            try:
                # Connect, set up notifications
                d = NUSRXDelegate()
                d.setChainsService(self)
                self.peripheral = btle.Peripheral(self.address, "random")
                self.peripheral.setDelegate(d)
                nus = self.peripheral.getServiceByUUID(btle.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E"))
                self.nustx = nus.getCharacteristics(btle.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"))[0]
                self.nusrx = nus.getCharacteristics(btle.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"))[0]
                self.nusrxnotifyhandle = self.nusrx.getHandle() + 1

                log.info('connected communications')
                break

            except btle.BTLEDisconnectError:
                log.info('BT connect failed, will retry in 3')
                time.sleep(3)

    def btUpload(self):

        # Initial program
        # @todo: relative path
        progFile = '/srv/chains/lib/chains/services/espruino/program.js'
        fp = open(progFile, 'r')
        progData = fp.read()
        fp.close()
        log.info('read initial program')
        self.sendProgram(progData)
        log.info('sent initial program')

    def onStart(self):
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

    def queueProgram(self, commands):
        log.info('queue prog: %s' % commands)
        self.programQueue.append(commands)

    # re-program puck.js
    def sendProgram(self, commands):
        # Format
        command = '\x03'
        for c in commands.split("\n"):
            c = c.strip()
            if not c: continue
            command += '\x10' + c + '\n'
        #log.info('sendProgram: %s' % command)
        #print command
        # Start
        self.peripheral.writeCharacteristic(self.nusrxnotifyhandle, b"\x01\x00", withResponse=True)
        # Send data (chunked to 20 bytes)
        while len(command)>0:
            self.nustx.write(command[0:20]);
            command = command[20:];

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

    def onShutdown(self):
        self.peripheral.disconnect()

    def sendEventWrapper(self, key, type, value):

        if type == 'i':
            try:
                value = int(value)
            except:
                log.error('failed converting int "%s" for key "%s"' % (value, key))
                value = -1
        if type == 'f':
            try:
                value = float(value)
            except:
                log.error('failed converting float "%s" for key "%s"' % (value, key))
                value = -1
        if type == 'b':
            if value in ['1',1,'true',True]:
                value = True
            else:
                value = False

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
