import chains.device, copy, re, td, Queue, time
from chains.common import log

# using: https://bitbucket.org/davka003/pytelldus/src

class TellstickDevice(chains.device.Device):

    def onInit(self):

        self.minLampValue          = 0
        self.maxLampValue          = 255
        self.repeatedEventTimeout  = 1
        self.repeatedEventLastTime = {}
        self.states                = {}

        log.info('Initializing td')

        td.init( defaultMethods = td.TELLSTICK_TURNON | td.TELLSTICK_TURNOFF | td.TELLSTICK_BELL | td.TELLSTICK_TOGGLE | td.TELLSTICK_DIM | td.TELLSTICK_LEARN )
        #td.debug = True

        log.info('Registering device event handler')
        td.registerDeviceEvent(self.deviceEventCallback)

        log.info('Registering sensor event handler')
        td.registerSensorEvent(self.sensorEventCallback)
        #td.registerRawDeviceEvent(...) # if we want to support ALL recvd signals. noisy!

        log.info('Initializing complete')

    def onShutdown(self):
        # Try to close libtelldus cleanly
        td.close()

    def action_dim(self, id, level):
        '''
        Dim a lamp to a specific level
        @param  id     int   ID of device in tellstick.conf
        @param  level  int   Light level (0-255)
        '''
        td.dim(self.parseId(id), self.parseLevel(level))

    def action_on(self, id):
        '''
        Turn a lamp on
        @param  id     int   ID of device in tellstick.conf
        '''
        td.turnOn(self.parseId(id))
        
    def action_off(self, id):
        '''
        Turn a lamp off
        @param  id     int   ID of device in tellstick.conf
        '''
        td.turnOff(self.parseId(id))

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
    # However, if dims are sent from this device, it will work.
    #
    # In short:
    # - For On/Off switches, you'll get correct state in chains even if you
    #   control them both from chains and external controllers.
    # - For dimmers, do it via Chains if you want correct state.
    #
    def deviceEventCallback(self, deviceId, method, value, callbackId):
        if self.ignoreRepeatedEvent(deviceId, method, value):
            return
        #log.info('DeviceCallback: %s : %s = %s' % (deviceId, method, value))
        if method == td.TELLSTICK_TURNON:
            self.sendLampEvent(deviceId, self.maxLampValue)
        elif method == td.TELLSTICK_TURNOFF:
            self.sendLampEvent(deviceId, self.minLampValue)
        elif method == td.TELLSTICK_DIM:
            self.sendLampEvent(deviceId, value)

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

    def sendSensorEvent(self, sensor):
        id = sensor['id']
        del sensor['id']
        self.sendEventWrapper('sensor-%s' % id, sensor)

    def sendLampEvent(self, id, value):
        key = 'lamp-%s' % id
        self.states[key] = value
        self.sendEventWrapper(key, { 'value': value })

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



    # Alias and suppress support - todo: make device-global?

    def sendEventWrapper(self, key, event):

        if self.shouldSuppressEvent(key):
            log.debug('Config says suppress event: %s' % key)
            return

        alias = self.getEventKeyAlias(key)
        if alias:
            log.debug('Change event key: %s to alias: %s' % (key, alias))
            key = alias

        self.sendEvent(key, event)


    def shouldSuppressEvent(self, key):
        suppressed = self.config.data('suppress')
        if suppressed and key in suppressed:
            return True
        else:
            return False

    def getEventKeyAlias(self, key):
        aliases = self.config.data('alias')
        if aliases and aliases.has_key(key):
            return aliases[key]

