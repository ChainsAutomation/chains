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
        zone.stop()

    def action_playUri(self, uri, zone=None):
        zone = self.getZone(zone)
        zone.play_uri(uri)

    def action_playPlaylist(self, name, zone=None):
        zone = self.getZone(zone)
        playlists = zone.get_sonos_playlists()
        if not playlists:
            return False
        found = None
        for playlist in playlists:
            if playlist.title.lower().strip() == name.lower().strip():
                found = playlist
                break
        if not found:
            return False
        zone.clear_queue()
        zone.add_to_queue(playlist)
        zone.play()

    def action_volume(self, volume, zone=None):
        zone = self.getZone(zone)
        zone.volume = int(volume)

    def action_getTrackInfo(self, zone=None):
        zone = self.getZone(zone)
        info = zone.get_current_track_info()
        del info['metadata']
        return info

    def action_getTrackMetaData(self, zone=None):
        zone = self.getZone(zone)
        info = zone.get_current_track_info()
        return info['metadata']

    def action_getTrackUri(self, zone=None):
        zone = self.getZone(zone)
        info = zone.get_current_track_info()
        if not info:
            return None
        return info.get('uri')

    def action_clearQueue(self, zone=None):
        zone = self.getZone(zone)
        zone.clear_queue()

