import chains.device
from chains.common import log

# Thanks to darrylb123 for figuring out how this device works:
# https://github.com/darrylb123/usbrelay

# Using python hidapi
# https://github.com/trezor/cython-hidapi
# pip install hidapi

import hid
import time

class USBRelayDevice(chains.device.Device):

    def onInit(self):
        self.ON = 255
        self.OFF = 253
        self.devices = self._find_devs()

    def _find_devs(self):
        devices = {}
        for d in hid.enumerate():
            if 'product_string' in d and d['product_string'].startswith('USBRelay'):
                ports = int(d['product_string'][8:])
                d.update({'ports': ports})
                d.update({'relays': range(1,ports + 1)})
                devices.update({ d['path']: d })
        return devices

    def _set_relay(self, rid, val, path=None):
        if not path:
            path = self.devices[self.devices.keys()[0]]['path']
        hdev = hid.device()
        hdev.open_path(path)
        hdev.write([0,val,rid,0,0,0,0,0,0])
        hdev.close()

    def _get_state(self, path=None):
        state = {}
        if not path:
            path = self.devices[self.devices.keys()[0]]['path']
        ports = self.devices[path]['ports']
        hdev = hid.device()
        hdev.open_path(path)
        info = hdev.get_feature_report(0x01,9)
        for cur in range(ports):
            if info[7] & 1 << cur:
                state.update({cur + 1 : 1})
            else:
                state.update({cur + 1 : 0})
        return state

    def action_on(self, rid, path=None):
        '''
        Turn a relay on
        @param  rid     int   Relay number
        @param  path     string   USB path
        '''
        self._set_relay(rid, self.ON, path)

    def action_off(self, rid, path=None):
        '''
        Turn a relay off
        @param  rid     int   Relay number
        @param  path     string   USB path
        '''
        self._set_relay(rid, self.OFF, path)

    def action_toggle(self, rid, path=None):
        '''
        Toggle a relay
        @param  rid     int   Relay number
        @param  path     string   USB path
        '''
        if not path:
            path = self.devices.keys()[0]['path']
        state = self._get_state(path)
        if state[rid]:
            self._set_relay(rid, self.OFF, path)
        else:
            self._set_relay(rid, self.ON, path)

