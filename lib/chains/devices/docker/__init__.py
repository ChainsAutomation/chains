from chains.device import Device
from chains.common import log
import requests

class DcokerDevice(Device):
    """Device implementing the push service on pushover.net"""

    def onInit(self):
        # Required parameters for pushover
        self.socketpath = self.config.get('socketpath')

    def action_containers(self):
        '''
        Get running containers

        '''
        pass

