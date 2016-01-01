from chains.service import Service
from chains.common import log

from .clifx import CLifx as CL

import time


class LifxService(Service):

    def onInit(self):
        # Let user define lamp locations in [lcations] section, label: location_name
        self.interval = self.config.getInt('interval') or 60
        self.num_lights = self.config.getInt('num_lights') or None
        self.lx = CL(self.num_lights)

    def onStart(self):
        log('Starting main lifx loop')
        while not self._shutdown:
            changes = self.lx.update_unit_info()
            if not (not changes['new'] and not changes['gone'] and not changes['changed']):
                self.send_change_events(changes)
            time.sleep(self.interval)

    def send_change_events(self, changes):
        for newbulb in changes['new']:
            pass
        for gonebulb in changes['gone']:
            pass
        for newbulb in changes['changed']:
            pass

    def lxevent(self, evtype, evmain, evmeta):
        pass

    def action_power_off(self, lamp):
        pass

    def action_power_on(self, lamp):
        pass

    def action_power_toggle(self, lamp):
        pass

    def action_all_on(self):
        pass

    def action_all_of(self):
        pass

    def action_set_color(self, color):
        pass
