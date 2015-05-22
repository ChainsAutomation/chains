#@depends bluez python-bluez

try:
    import bluetooth
except ImportError, e:
    raise Exception("Cannot import bluetooth module. Please install python-bluez")

import time, chains.device
from chains.common import log

class BtoothDevice(chains.device.Device):

    def onInit(self):
        self.interval = self.config.getInt('interval')
        self.goneTime = self.config.getInt('gonetime')
        guests = self.config.data('guests')
        if not guests:
            guests = {}
        self.state = {}
        self.guests = self.swapDict(guests)
        self.guestsToState()

    def onStart(self):
        while not self._shutdown:
            self.poll()
            time.sleep(self.interval)


    def poll(self):

        addresses = self.getBluetoothDevices()
        if not addresses:
            return

        # And process each of them
        for address in addresses:
            self.onDeviceSeen(address)

        # Check devices that are present in state, and
        # if it's long since we've seen any, consider
        # them as left
        now = time.time()
        for address in self.state:
            if self.state[address]['present']:
                if now > (self.state[address]['time'] + self.goneTime):
                    self.onDeviceLeft(address)

    def onDeviceSeen(self, address):
        isArrival = False
        if self.state.has_key(address):
            self.state[address]['time'] = time.time()
            if not self.state[address]['present']:
                isArrival = True
                self.state[address]['present'] = True
            else:
                return
        else:
            isArrival = True
            self.addToState(address, True)
        if isArrival:
            self.onDeviceArrived(address)

    def onDeviceArrived(self, address):

        # Lookup bluetooth name if not already set
        if not self.state[address].get('name'):
            try:
                name = bluetooth.lookup_name(address)
            except:
                name = 'Unknown'
            self.state[address]['name'] = name

        self.sendDeviceChange(address, True)

    def onDeviceLeft(self, address):

        self.state[address]['present'] = False
        self.state[address]['time'] = time.time()

        self.sendDeviceChange(address, False)

    def sendDeviceChange(self, address, value):

        name = self.state[address]['name']
        nick = self.state[address]['nick']

        known = False
        key   = address
        if address in self.guests:
            known = True
            key   = nick

        self.sendEvent('presence-%s' % key, {
            'address': address,
            'name':    name,
            'nick':    nick,
            'known':   known,
            'value':   value
        })

        present = 0
        away    = 0
        some    = False

        for address, nick in self.guests.iteritems():
            state = self.state.get(address)
            if state and state['present']:
                present += 1
            else:
                away += 1

        if present > 0:
            some = True

        self.sendEvent('presence-summary', {
            'present': present,
            'away':    away,
            'value':   some
        })

        log.info('foo')

    def getBluetoothDevices(self):
        log.debug('Getting bluetooth devices')
        result = []

        if self.config.getBool('discover'):
            log.debug('Using devices_discover() to find devices')
            try:
                for addr in bluetooth.discover_devices(flush_cache=True):
                    log.debug('Found device: %s' % addr)
                    result.append(addr)
            # This happens from time to time, and we don't want to die because of it:
            # BluetoothError: error communicating with local bluetooth adapter
            except bluetooth.btcommon.BluetoothError,e:
                log.warn('BluetoothError ignored: %s' % e)
        else:
            log.debug('Not configured to use devices_discover() to find devices')

        if self.config.getBool('lookup'):
            log.debug('Using lookup_name() to find devices')
            try:
                for addr in self.guests:
                    name = bluetooth.lookup_name(addr)
                    if name:
                        log.debug('Found device: %s' % addr)
                        result.append(addr)
                    else:
                        log.debug('Did not find device: %s' % addr)
            # This happens from time to time, and we don't want to die because of it:
            # BluetoothError: error communicating with local bluetooth adapter
            except bluetooth.btcommon.BluetoothError,e:
                log.warn('BluetoothError ignored: %s' % e)
        else:
            log.debug('Not configured to use lookup_name() to find devices')

        log.debug('Finished getting blueooth devices')

        return result

    def guestsToState(self):
        for mac, nick in self.guests.iteritems():
            self.addToState(mac, False, nick)

    def addToState(self, address, present, nick=None):
        self.state[address] = {
            'name': None,         # name that device identifies itself by via bluetooth
            'nick': nick,         # friendly name for guest from config
            'present': present,   # whether device is present now or not
            'time': time.time()   # last time state was updated
        }

    def swapDict(self,guests):
        return dict((mac, name) for (name, mac) in guests.items())



