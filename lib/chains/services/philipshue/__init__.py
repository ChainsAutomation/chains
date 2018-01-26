from __future__ import absolute_import

import chains.service
from chains.common import log

# NB: Removed this and placed pyhue.py inside service dir
# Because needed to fix a bug with encoding causing special chars in lamp texts to fail
# ---
# https://github.com/aleroddepaz/pyhue
# pip install pyhue
#import pyhue

from chains.services.philipshue import pyhue

import time

class PhilipsHueService(chains.service.Service):

    def onInit(self):
        self.location = self.config.get('location')
        self.didInitialConnect = False
        #self.hueConnect()
        #self.sendStartupEvents()

    def hueConnect(self):
        address, username = self.getBridgeConfig()
        log.info("Connect to bridge: %s @ %s" % (username, address))
        self.bridge = pyhue.Bridge(address, username)

    def onStart(self):
        while not self._shutdown:
            connected = False
            try:
                self.bridge.lights #get_light('1')
                connected = True
            except:
                try:
                    self.hueConnect()
                    log.info('Successfully connected to bridge')
                except: # pyhue.HueException, e:
                    log.warn('Connect to bridge failed: %s' % e)
            if connected:
                if not self.didInitialConnect:
                    self.didInitialConnect = True
                    self.sendStartupEvents()
            time.sleep(5)

    def action_on(self, id):
        '''
        Turn a lamp on
        @param  id     int   ID
        '''
        self.getLight(id).on = True

    def action_off(self, id):
        '''
        Turn a lamp off
        @param  id     int   ID
        '''
        self.getLight(id).on = False

    def action_dim(self, id, level):
        '''
        Dim a lamp
        @param  id     int   ID
        @param  level  int   Brightness
        '''
        self.getLight(id).on  = True
        self.getLight(id).bri = self.parseLevel(level)

    def action_hue(self, id, hue):
        self.getLight(id).on  = True
        self.getLight(id).hue = self.parseHue(hue)

    def action_saturation(self, id, saturation):
        self.getLight(id).on  = True
        self.getLight(id).sat = self.parseLevel(saturation)

    def action_alert(self, id, enable):
        self.getLight(id).on = True
        if enable:
            self.getLight(id).alert = 'lselect'
        else:
            self.getLight(id).alert = 'none'

    def action_effect(self, id, enable):
        self.getLight(id).on = True
        if enable:
            self.getLight(id).effect = 'colorloop'
        else:
            self.getLight(id).effect = 'none'

    def action_state(self, id, state):
        light = self.getLight(id)
        light.on = True
        keys = ['bri','sat','hue','effect','xy','ct','alert','colormode']
        for key in keys:
            try:
                value = state[key]
            except KeyError:
                continue
            setattr(light, key, value)

    def action_get(self, id):
        light = self.getLight(id)
        item = {
            'id':    light.id,
            'name':  light.name,
            'type':  light.type,
            'model': light.modelid,
        }
        for key in light.state:
            item[key] = light.state[key]
        return item

    def action_list(self):
        '''
        List available lamps
        '''
        result = []
        for light in self.bridge.lights:
            item = {
                'id':    light.id,
                'name':  light.name,
                'type':  light.type,
                'model': light.modelid,
            }
            for key in light.state:
                item[key] = light.state[key]
            result.append(item)
        return result

    def action_rename(self, id, name):
        if name:
            light = self.getLight(id)
            light.name = name

    def getBridgeConfig(self):
        address = self.config.get('address')
        username = self.config.get('username')
        if not address:
            raise Exception('Must configure address = <ip> or "auto" under [main] in config')
        if not username:
            raise Exception('Must configure username = <username-for-hue-bridge> under [main] in config')
        if address == 'auto':
            from chains.services.philipshue import discovery
            info = discovery.discover()
            if info:
                info = info[0] # todo: handle multiple bridges? 
            if info and 'internalipaddress' in info:
                address = info['internalipaddress']
                log.info('discovered bridge-address: %s' % address)
            else:
                log.warn('could not find bridge-address by auto-discovery')
        else:
            log.info('got bridge-address from config: %s' % address)
        return (address, username)

    def getLight(self, id):
        id    = self.parseId(id)
        light = self.bridge.get_light(id)
        if not light:
            raise Exception('No light with id: %s' % id)
        return light

    def parseId(self, id):
        return str(id)

    def parseLevel(self, level):
        try:
            level = int(level)
        except:
            return 0
        if level < 0:
            level = 0
        elif level > 255:
            level = 255
        return level

    # 0 red, 25500 green, 46920 blue, 65535 red
    def parseHue(self, level):
        try:
            level = int(level)
        except:
            return 0
        if level < 0:
            level = 0
        elif level > 65535:
            level = 65535
        return level

    """
    def sendLampEvent(self, id, value):
        self.sendEvent(id, { 'value': value })

    def parseFloat(self, value):
        if value == None:
            return 0
        else:
            return float(value)
    """

    def sendStartupEvents(self):
        for light in self.bridge.lights:
            item = {
                'id':    light.id,
                'name':  light.name,
                'type':  light.type,
                'model': light.modelid,
            }
            for key in light.state:
                item[key] = light.state[key]
            item['type'] = 'lamp'
            item['value'] = item.get('bri')
            meta = {'type': 'lamp'} # type goes in devattribs, remove the above later?
            if self.location:
                meta.update({'location': self.location})
            if not item.get('on'):
                item['value'] = 0
            meta.update({'device': 'lamp-%s' % item['id']})
            for key, value in item.items():
                item[key] = {'value': value}
            self.sendEvent('change', item, meta)
