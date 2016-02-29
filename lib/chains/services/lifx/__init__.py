from __future__ import absolute_import

from chains.service import Service
from chains.common import log

from .clifx import CLifx as CL

import time


class LifxService(Service):

    def onInit(self):
        # TODO: Let user define lamp locations in [lcations] section, label: location_name
        self.interval = self.config.getInt('interval') or 60
        self.num_lights = self.config.getInt('num_lights') or None
        self.lx = CL(self.num_lights)

    def onStart(self):
        log.info('Starting main lifx loop')
        while not self._shutdown:
            changes = self.lx.update_unit_info()
            if not (not changes['new'] and not changes['gone'] and not changes['changed']):
                self.send_change_events(changes)
            time.sleep(self.interval)

    def send_change_events(self, changes):
        meta = {'type': 'lamp'}
        for newbulb in changes['new']:
            meta['device'] = newbulb
            self.sendEvent('new_lamp', self.cdictify(changes['new'][newbulb]), meta)
        for gonebulb in changes['gone']:
            meta['device'] = gonebulb
            self.sendEvent('gone_lamp', {}, meta)
        for changedbulb in changes['changed']:
            meta['device'] = changedbulb
            self.sendEvent('changed_lamp', self.cdictify(changes['changed'][changedbulb]), meta)

    def lxevent(self, evtype, evmain, evmeta):
        pass

    def action_power_off(self, lamp):
        pass

    def action_power_on(self, lamp):
        pass

    def action_power_toggle(self, lamp):
        pass

    def action_all_on(self):
        '''
        Turn all lamps off
        '''

    def action_all_off(self):
        '''
        Turn all lamps off
        '''

    def action_set_color(self, color):
        pass

    def cdictify(self, flat_dict):
        cdict = {}
        for key, value in flat_dict.items():
            cdict.update({key: {'value': value}})
        return cdict
