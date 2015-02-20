#@depends bluez python-bluez

try:
    import bluetooth
except ImportError, e:
    raise Exception("Cannot import bluetooth module. Please install python-bluez")

import time, chains.device
from chains.common import log

'''
@todo: describe events
    * <MAC> - True/False
    * GuestLeft - <MAC>
    * UnknownLeft <MAC>
    * GuestArrive <MAC>
    * UnknownArrive <MAC>
    * ALLGuestsGone
@todo: implement rest of device (actions) - sms, position, obex, etc
    * See old device in branches/0.2
'''

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

        # Fetch MAC addresses for all nearby devices
        addresses = self.getBluetoothDevices()
        if not addresses:
            return

        presentGuestDeviceCountBefore = self.getPresentGuestDeviceCount()
        presentUnknownDeviceCountBefore = self.getPresentUnknownDeviceCount()

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

        # If all guests left, fire AllGuestsGone event
        if presentGuestDeviceCountBefore > 0 and self.getPresentGuestDeviceCount() == 0:
            self.sendEvent('AllGuestsGone', {'value':True})

        # If all unknowns left, fire AllUnknownsGone event
        if presentUnknownDeviceCountBefore > 0 and self.getPresentUnknownDeviceCount() == 0:
            self.sendEvent('AllUnknownsGone', {'value':True})

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
        if not self.state[address]['name']:
            try:
                name = bluetooth.lookup_name(address)
            except:
                name = 'Unknown'
            self.state[address]['name'] = name
        name = self.state[address]['name']
        nick = self.state[address]['nick']

        # Send arrival events
        isGuest = (address in self.guests)
        if isGuest:
            self.sendEvent('GuestArrived',      {'address': address, 'name': name, 'nick': nick})
            self.sendEvent('Guest-%s' % nick,   {'address': address, 'name': name, 'nick': nick, 'value': True})
            # Do we really need this?
            #if self.getPresentGuestDeviceCount() == 1:
            #    self.sendEvent('FirstGuest',    {'address': address, 'name': name, 'nick': nick})
        else:
            self.sendEvent('UnknownArrived',    {'address': address, 'name': name})
            self.sendEvent('Unknown-%s' % name, {'address': address, 'name': name, 'value': True})
            # Do we really need this?
            #if self.getPresentUnknownDeviceCount() == 1:
            #    self.sendEvent('FirstUnknown',  {'address': address, 'name': name})

    def onDeviceLeft(self, address):
        isGuest = (address in self.guests)
        name = self.state[address]['name']
        nick = self.state[address]['nick']
        if isGuest:
            self.sendEvent('GuestLeft',         {'address': address, 'name': name, 'nick': nick})
            self.sendEvent('Guest-%s' % nick,   {'address': address, 'name': name, 'nick': nick, 'value': False})
        else:
            self.sendEvent('UnknownLeft',       {'address': address, 'name': name})
            self.sendEvent('Unknown-%s' % name, {'address': address, 'name': name, 'value': False})
        self.state[address]['present'] = False
        self.state[address]['time'] = time.time()

    def getPresentDeviceCount(self, isGuest=None):
        n = 0
        for address in self.state:
            item = self.state[address]
            if isGuest in [True,False]:
                isGuest2 = (address in self.guests)
                if isGuest2 != isGuest:
                    continue
            if item['present']:
                n += 1
        return n

    def getPresentGuestDeviceCount(self):
        return self.getPresentDeviceCount(isGuest=True)
    def getPresentUnknownDeviceCount(self):
        return self.getPresentDeviceCount(isGuest=False)

    def getBluetoothDevices(self):
        try:
            return bluetooth.discover_devices(flush_cache=True)
        # This happens from time to time, and we don't want to die because of it:
        # BluetoothError: error communicating with local bluetooth adapter
        except bluetooth.BluetoothError,e:
            log.warn('BluetoothError ignored: %s' % e)
            return []

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



