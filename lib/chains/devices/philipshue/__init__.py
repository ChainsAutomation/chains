import chains.device
from chains.common import log

# https://github.com/aleroddepaz/pyhue
# pip install pyhue
import pyhue

class PhilipsHueDevice(chains.device.Device):

    def onInit(self):
        address, username = self.getBridgeConfig()
        self.bridge = pyhue.Bridge(address, username)

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
        self.getLight(id).on = True
        for key in state:
            setattr(light, key, state[key])

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
            raise Exception('Must configure address = <ip-of-hue-bridge> under [main] in config')
        if not username:
            raise Exception('Must configure username = <username-for-hue-bridge> under [main] in config')
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

