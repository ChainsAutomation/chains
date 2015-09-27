import chains.service, copy, re, td, Queue, time
from chains.common import log
import time

# using: https://bitbucket.org/davka003/pytelldus/src

class TellstickService(chains.service.Service):

    def onInit(self):

        self.minLampValue          = 0
        self.maxLampValue          = 255
        self.repeatedEventTimeout  = 1
        self.repeatedEventLastTime = {}
        self.states                = {}

        self.eventCallbackId = None
        self.sensorCallbackId = None

        log.info('Open telldus')
        self.openTelldus()
        log.info('Opened telldus')

        self.devices = self.parseDeviceConfig()


    def onShutdown(self):
        self.closeTelldus()

    def action_dim(self, id, level):
        '''
        Dim a lamp to a specific level
        @param  id     int   ID of device in tellstick.conf
        @param  level  int   Light level (0-255)
        '''
        id = self.parseId(id)
        level = self.parseLevel(level)
        td.dim(id, level)
        self.sendDeviceEvent(id, level)

    def action_on(self, id):
        '''
        Turn a lamp on
        @param  id     int   ID of device in tellstick.conf
        '''
        id = self.parseId(id)
        td.turnOn(id)
        self.sendDeviceEvent(id, self.maxLampValue)
        
    def action_off(self, id):
        '''
        Turn a lamp off
        @param  id     int   ID of device in tellstick.conf
        '''
        id = self.parseId(id)
        td.turnOff(id)
        self.sendDeviceEvent(id, self.minLampValue)

    # Skip these, at least until someone requests them, since
    # we want to avoid this kind of uncontrolled dimming
    # which cause us to not be able to keep track of state.
    """
    def action_up(self, id):
        '''
        Start dimming a lamp up
        @param  id     int   ID of device in tellstick.conf
        '''
        td.up(self.parseId(id))
        
    def action_down(self, id):
        '''
        Start dimming a lamp down
        @param  id     int   ID of device in tellstick.conf
        '''
        td.down(self.parseId(id))

    def action_stop(self, id):
        '''
        Stop dimming a lamp up or down
        @param  id     int   ID of device in tellstick.conf
        '''
        td.stop(self.parseId(id))
    """

    def action_bell(self, id):
        '''
        Send bell signal for a lamp
        @param  id     int   ID of device in tellstick.conf
        '''
        td.bell(self.parseId(id))

    def action_learn(self, id):
        '''
        Send learn signal for a lamp
        @param  id     int   ID of device in tellstick.conf
        '''
        td.learn(self.parseId(id))

    def action_list(self):
        '''
        List available devices, and return result like this:
           [
            {'id': 1, 'name': 'office_roof',       'value': 250 },
            {'id': 1, 'name': 'livingroom_corner', 'value': 255 },
           ]
        '''
        result = [] 
        for i in range(td.getNumberOfDevices()):
           id = td.getDeviceId(i)
           result.append({
               'id':    id,
               'name':  td.getName(id),
               'value': self.states.get('lamp-%s' % id)
           })
        return result

    def action_tdreset(self):
        self.closeTelldus()
        time.sleep(1)
        self.openTelldus()

    # Note about dimming and external controllers:
    #
    # Tellstick Duo will receive on/off events from external controllers,
    # but not dim events. Also, some controllers leaves dimming to receiver.
    #
    #  - turnon(1)   User clicks wall switch, receiver turns on
    #  - turnon(1)   User clicks wall switch again, receiver start dimming
    #  - turnon(1)   User clicks wall switch again, receiver stops dimming
    #
    # To properly infer a resulting dimming value from these events would
    # be a nightmare (require us to know what state the lamp was in before, 
    # how fast it dims, how much latency there is before we receive the event).
    # So we won't try that.
    #
    # However, if dims are sent from this service, it will work.
    #
    # In short:
    # - For On/Off switches, you'll get correct state in chains even if you
    #   control them both from chains and external controllers.
    # - For dimmers, do it via Chains if you want correct state.
    #
    def deviceEventCallback(self, deviceId, method, value, callbackId):
        if self.ignoreRepeatedEvent(deviceId, method, value):
            return
        if method == td.TELLSTICK_TURNON:
            self.sendDeviceEvent(deviceId, self.maxLampValue)
        elif method == td.TELLSTICK_TURNOFF:
            self.sendDeviceEvent(deviceId, self.minLampValue)
        elif method == td.TELLSTICK_DIM:
            self.sendDeviceEvent(deviceId, value)

    def sensorEventCallback(self, protocol, model, sensorId, dataType, value, timestamp, callbackId):
        if dataType == td.TELLSTICK_TEMPERATURE:
            typeText = 'temperature'
            value    = self.parseFloat(value)
        elif dataType == td.TELLSTICK_HUMIDITY:
            typeText = 'humidity'
            value    = self.parseFloat(value)
        elif dataType != None:
            typeText = 'unknown:%s' % dataType
        else:
            typeText = None
        self.sendSensorEvent({
            'id':       '%s-%s' % (sensorId, dataType),
            'value':    value,
            'type':     typeText,
            'protocol': protocol,
            'model':    model,
            'time':     timestamp
        })

    def parseId(self, id):
        return int(id)

    def parseLevel(self, level):
        return int(level)

    def parseFloat(self, value):
        if value == None:
            return 0
        else:
            return float(value)

    # Remotes typically send a handful of the same event,
    # as to "make sure at least one arrive". So when we receive
    # a many of the same event within a short time, we want to
    # filter out just one of them.
    def ignoreRepeatedEvent(self, deviceId, method, value):
        key = '%s.%s.%s' % (deviceId, method, value)
        now = time.time()
        if self.repeatedEventLastTime.has_key(key):
            timeDiff = now - self.repeatedEventLastTime[key]
            if timeDiff < self.repeatedEventTimeout:
                return True
        self.repeatedEventLastTime[key] = now


    def sendSensorEvent(self, sensor):
        id = sensor['id']
        del sensor['id']
        self.sendEventWrapper('sensor', id, sensor)

    def sendDeviceEvent(self, id, value):
        key = 'device-%s' % id
        self.states[key] = value
        self.sendEventWrapper('device', id, { 'value': value })

    def sendEventWrapper(self, type, id, event):

        device = '%s-%s' % (type,id)
        config = self.devices.get(device)
        if config:
            if config.get('suppress'):
                log.debug('Config says suppress event: %s' % device)
                return
            if config.get('id'):
                device = config.get('id')
            if config.get('name'):
                event['name'] = config.get('name')
            if config.get('location'):
                event['location'] = config.get('location')
            # todo: infer these from telldus types instead (done for sensor, todo for device)
            if config.get('type') and not event.get('type'):
                event['type'] = config.get('type')
            elif type == 'device':
                event['type'] = 'lamp'
            
        self.sendEvent('change', event, device)

    def openTelldus(self):

        log.info('Opening telldus')

        td.init( defaultMethods = td.TELLSTICK_TURNON | td.TELLSTICK_TURNOFF | td.TELLSTICK_BELL | td.TELLSTICK_TOGGLE | td.TELLSTICK_DIM | td.TELLSTICK_LEARN )
        #td.debug = True

        log.info('Registering device event handler')
        self.deviceCallbackId = td.registerDeviceEvent(self.deviceEventCallback)

        log.info('Registering sensor event handler')
        self.sensorCallbackId = td.registerSensorEvent(self.sensorEventCallback)
        #td.registerRawDeviceEvent(...) # if we want to support ALL recvd signals. noisy!

        log.info('Initializing complete')

    def closeTelldus(self):

        log.info('Closing telldus')

        try:
            td.unregisterCallback(self.deviceCallbackId)
        except:
            log.warn('ignored error unregistering device callback')

        try:
            td.unregisterCallback(self.sensorCallbackId)
        except:
            log.warn('ignored error unregistering sensor callback')

        try:
            td.close()
        except:
            log.warn('ignored error closing td')

    def parseDeviceConfig(self):
        result = {}
        conf = self.config.data('devices')
        if conf:
            for key in conf:
                deviceId, prop = key.split('.')
                if not result.has_key(deviceId):
                    result[deviceId] = {
                        'id': deviceId,
                        'location': None,
                        'name': None,
                        'suppress': False
                    }
                value = conf[key]
                if prop == 'suppress':
                    if value.lower() in ['1','true']:
                        value = True
                    else:
                        value = False
                result[deviceId][prop] = value
        return result

