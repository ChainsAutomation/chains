from chains.service import Service
from chains.common import log
import requests

class DcokerService(Service):
    """Service implementing the push service on pushover.net"""

    def onInit(self):
        # Required parameters for pushover
        self.socketpath = self.config.get('socketpath')

    def action_containers(self):
        '''
        Get running containers

        '''
        pass

