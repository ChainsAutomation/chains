# apt-get install -y bluez libglib2.0-dev
# pip install bluepy

from __future__ import absolute_import
import chains.service
from chains.common import log
import time, datetime, re, copy
import time

# Receiver for notifications on this side
class NUSRXDelegate(btle.DefaultDelegate):
    def __init__(self):
        self.chainsService = None
        btle.DefaultDelegate.__init__(self)
        # ... initialise here
    def handleNotification(self, cHandle, data):
        log.info('EspruinoService.NUSRXDelegate.RX:', data)
    def __handleNotification(self, cHandle, data):
        print('RX: ', data)
        try:
            if data.find('BTN') > -1:
                tmp = data.split('BTN ')
                val = float(tmp[1])
                print('VAL:', val)
                if val > 1:
                    program('LED2.toggle()')
        except:
            print "err"
    def setChainsService(self, service):
        self.chainsService = service

class EspruinoService(chains.service.Service):

    def onInit(self):

        log.info('Starting EspruinoService')
        self.address = self.config.get('puckaddress') # NRF.getAddress() on Puck console
        log.info('address = %s' % self.address)

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
            time.sleep(1)

    # re-program puck.js
    def sendProgram(self, commands):
        # Format
        command = '\x03'
        for c in commands.split("\n"):
            c = c.strip()
            if not c: continue
            command += '\x10' + c + '\n'
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
        toggleString = 'false'
        if toggle:
            toggleString = 'true'
        self.sendProgram('setBlink(%s, %s);' % (index, toggleString))

    """
    def onShutdown(self):
        if self.interval:
            self.interval.cancel()

        self.deRegisterForEvents()

        event_listener.stop()
    """
