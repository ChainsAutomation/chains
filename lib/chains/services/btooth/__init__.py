#@depends bluez python-bluez
from __future__ import absolute_import
import six

try:
    import bluetooth
except ImportError as e:
    raise Exception("Cannot import bluetooth module. Please install python-bluez")

import time, chains.service
from chains.common import log

class BtoothService(chains.service.Service):

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

        addresses = self.getBluetoothServices()
        if not addresses:
            return

        # And process each of them
        for address in addresses:
            self.onServiceSeen(address)

        # Check services that are present in state, and
        # if it's long since we've seen any, consider
        # them as left
        now = time.time()
        for address in self.state:
            if self.state[address]['present']:
                if now > (self.state[address]['time'] + self.goneTime):
                    self.onServiceLeft(address)

    def onServiceSeen(self, address):
        isArrival = False
        if address in self.state:
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
            self.onServiceArrived(address)

    def onServiceArrived(self, address):

        # Lookup bluetooth name if not already set
        if not self.state[address].get('name'):
            try:
                name = bluetooth.lookup_name(address)
            except:
                name = 'Unknown'
            self.state[address]['name'] = name

        self.sendServiceChange(address, True)

    def onServiceLeft(self, address):

        self.state[address]['present'] = False
        self.state[address]['time'] = time.time()

        self.sendServiceChange(address, False)

    def sendServiceChange(self, address, value):

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

        for address, nick in six.iteritems(self.guests):
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

    def getBluetoothServices(self):
        log.debug('Getting bluetooth services')
        result = []

        if self.config.getBool('discover'):
            log.debug('Using services_discover() to find services')
            try:
                for addr in bluetooth.discover_services(flush_cache=True):
                    log.debug('Found service: %s' % addr)
                    result.append(addr)
            # This happens from time to time, and we don't want to die because of it:
            # BluetoothError: error communicating with local bluetooth adapter
            except bluetooth.btcommon.BluetoothError as e:
                log.warn('BluetoothError ignored: %s' % e)
        else:
            log.debug('Not configured to use services_discover() to find services')

        if self.config.getBool('lookup'):
            log.debug('Using lookup_name() to find services')
            try:
                for addr in self.guests:
                    name = bluetooth.lookup_name(addr)
                    if name:
                        log.debug('Found service: %s' % addr)
                        result.append(addr)
                    else:
                        log.debug('Did not find service: %s' % addr)
            # This happens from time to time, and we don't want to die because of it:
            # BluetoothError: error communicating with local bluetooth adapter
            except bluetooth.btcommon.BluetoothError as e:
                log.warn('BluetoothError ignored: %s' % e)
        else:
            log.debug('Not configured to use lookup_name() to find services')

        log.debug('Finished getting blueooth services')

        return result

    def guestsToState(self):
        for mac, nick in six.iteritems(self.guests):
            self.addToState(mac, False, nick)

    def addToState(self, address, present, nick=None):
        self.state[address] = {
            'name': None,         # name that service identifies itself by via bluetooth
            'nick': nick,         # friendly name for guest from config
            'present': present,   # whether service is present now or not
            'time': time.time()   # last time state was updated
        }

    def swapDict(self,guests):
        return dict((mac, name) for (name, mac) in guests.items())



