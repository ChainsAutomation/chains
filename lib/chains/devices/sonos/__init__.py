import chains.device
from chains.common import log
import time, datetime, re, copy
from soco import SoCo, discover

class SonosDevice(chains.device.Device):

    def onInit(self):

        # Discover Sonos players
        self.zones = list(discover())

        # Set default player
        self.defaultZone = None
        if self.zones:
            defaultZone = self.config.get('defaultzone')
            if defaultZone:
                self.defaultZone = self.getZone(defaultZone)
            else:
                self.defaultZone = self.zones[0]
            
        

    def getZone(self, nameOrId):
        for zone in self.zones:
            if zone.uid == nameOrId:
                return zone
            if zone.player_name == nameOrId:
                return zone
        return self.defaultZone

    def action_play(self, zone=None):
        zone = self.getZone(zone)
        zone.play()

    def action_stop(self, zone=None):
        zone = self.getZone(zone)
        zone.play()

    def action_playUri(self, uri, zone=None):
        zone = self.getZone(zone)
        zone.play_uri(uri)

    def action_volume(self, volume, zone=None):
        zone = self.getZone(zone)
        zone.volume = int(volume)
