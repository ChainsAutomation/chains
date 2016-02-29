from __future__ import absolute_import
from __future__ import print_function

from lifxlan import *


class CLifx(object):

    pwr_str = {'0': 'Off', '65535': 'On'}

    def __init__(self, num_units=None):
        self.num_units = num_units
        self.state = {}

    def _find_units(self):
        lifx = LifxLAN(self.num_units)
        lights = lifx.get_lights()
        return lights

    def update_unit_info(self):
        units_up = {}
        changes = {'new': [], 'gone': [], 'changed': {}}
        info = ['label', 'mac_address', 'ip_address', 'port', 'power']
        lights = self._find_units()
        for dev in lights:
            signal, tx, rx = dev.get_wifi_info_tuple()
            units_up.update({dev.mac_addr: {
                'ip_address': dev.ip_addr,
                'label': dev.get_label(),
                'mac_address': dev.mac_addr,
                'port': dev.port,
                'power': self.pwr_str[str(dev.get_power())],
                'wifi_firmware': dev.get_wifi_firmware_tuple()[1],
                'firmware': dev.get_host_firmware_tuple()[1],
                'uptime': dev.get_info_tuple()[1] / 1000000000 / 60,
                'wifi_signal': signal,
                'wifi_rx': rx,
                'wifi_tx': tx
            }})
        for smac in self.state:
            if smac not in units_up:
                changes['gone'].append(smac)
                del(self.state[smac])
        for mac in units_up:
            if mac not in self.state:
                changes['new'].append(mac)
            else:
                print(mac + " is in state:")
                print(self.state[mac])
                for i in info:
                    if not units_up[mac][i] == self.state[mac][i]:
                        if mac not in changes['changed']:
                            changes['changed'].update({mac: []})
                        changes['changed'][mac].append(i)
        self.state = units_up
        return changes

    def all_off(self):
        set_power_all_lights(power, [duration], [rapid])

if __name__ == '__main__':
    lx = CLifx()
    devs = lx._find_units()
    for d in devs:
        print(d)
    print("State:")
    print(lx.state)
    print('Updating state:')
    ch = lx.update_unit_info()
    print("Changes:")
    print(ch)
    print("State:")
    print(lx.state)
    print('Updating again:')
    ch = lx.update_unit_info()
    print("Changes:")
    print(ch)
