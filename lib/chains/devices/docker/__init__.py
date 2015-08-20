from chains.device import Device
from chains.common import log
import requests
from . import docker

class DcokerDevice(Device):
    """Device implementing the push service on pushover.net"""

    def onInit(self):
        # Required parameters for pushover
        self.socketpath = self.config.get('socketpath') or '/var/run/docker.sock'
        # TODO set params for dockercon
        self.dockercon = docker.Docker()


    def onStart(self):
        while not self._shutdown:
            self.dockercon.reader()

    def action_containers(self):
        '''
        Get running containers

        '''
        pass

