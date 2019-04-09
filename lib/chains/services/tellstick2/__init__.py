import chains.service, copy, re, td, Queue, time
from chains.services.tellstick2 import tellconf
from chains.common import log, utils
import time, subprocess

# using: https://bitbucket.org/davka003/pytelldus/src

class Tellstick2Service(chains.service.Service):

    def onInit(self):

        self.minLampValue          = 0
        self.maxLampValue          = 255
        self.repeatedEventTimeout  = 1
        self.repeatedEventLastTime = {}
        self.states                = {}
        self.suppressUnconfigured  = False
        if self.config.get('suppressunconfigured') and self.config.get('suppressunconfigured') not in [0,'0','false',False]:
            self.suppressUnconfigured = True

        self.eventCallbackId = None
        self.sensorCallbackId = None

        self.devices = self.parseDeviceConfig()
        if self.config.getBool('managetellstickconf'):
            tellconf1 = self.readTellstickConf()
            self.writeTellstickConf()
            tellconf2 = self.readTellstickConf()
            if tellconf1 != tellconf2:
                log.info('Restart telldus since config changed')
                self.restartTelldus() # todo: only if there is a change
            else:
                log.info('Do not restart telldus since config did not change')

        self.openTelldus()

        if self.config.getBool('sendstartupevents'):
            self.sendStartupEvents()


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
        self.deviceEventCallback(id, td.TELLSTICK_DIM, level, 1)

    def action_on(self, id):
        '''
        Turn a lamp on
        @param  id     int   ID of device in tellstick.conf
        '''
        id = self.parseId(id)
        td.turnOn(id)
        self.deviceEventCallback(id, td.TELLSTICK_TURNON, self.maxLampValue, 1)
        
    def action_off(self, id):
        '''
        Turn a lamp off
        @param  id     int   ID of device in tellstick.conf
        '''
        id = self.parseId(id)
        td.turnOff(id)
        self.deviceEventCallback(id, td.TELLSTICK_TURNOFF, self.minLampValue, 1)

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

    def action_id(self, id):
        return self.parseId(id)

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
    def deviceEventCallback(self, deviceId, method, value, callbackId, isStartup=False):
        if self.ignoreRepeatedEvent(deviceId, method, value):
            return
        self.states['device-%s' % deviceId] = value
        if method == td.TELLSTICK_TURNON:
            self.sendEventWrapper('device', deviceId, {
                'state': {'value': 'on'},
                'brightness': {'value': self.maxLampValue}
            }, { 'ignore': isStartup })
        elif method == td.TELLSTICK_TURNOFF:
            self.sendEventWrapper('device', deviceId, {
                'state': {'value': 'off'},
                'brightness': {'value': self.minLampValue}
            }, { 'ignore': isStartup })
        elif method == td.TELLSTICK_DIM:
            state = 'on'
            if value == self.minLampValue:
                state = 'off'
            self.sendEventWrapper('device', deviceId, {
                'state': {'value': state},
                'brightness': {'value': value}
            }, { 'ignore': isStartup })

    def sensorEventCallback(self, protocol, model, sensorId, dataType, value, timestamp, callbackId, isStartup=False):
        if dataType == td.TELLSTICK_TEMPERATURE:
            typeText = 'temperature'
            value    = self.parseFloat(value)
        elif dataType == td.TELLSTICK_HUMIDITY:
            typeText = 'humidity'
            value    = self.parseFloat(value)
        elif dataType != None:
            typeText = 'unknown-%s' % dataType
        else:
            typeText = None
        self.sendEventWrapper(
            'sensor', 
            '%s-%s' % (sensorId,dataType), 
            {
                typeText:   { 'value': value },
            },
            {
                'type':     typeText,
                'protocol': protocol,
                'model':    model,
                'ignore':   isStartup
            }
        )

    def parseId(self, id):
        try:
            return int(id)
        except ValueError:
            for devId in self.devices:
                if devId == id and self.devices[devId].get('id'):
                    return int(self.devices[devId]['id'])
        raise Exception('Not found: %s' % id)

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


    def sendEventWrapper(self, type, id, data, deviceAttributes=None):
        try:
            self._sendEventWrapper(type, id, data, deviceAttributes)
        except Exception, e:
            log.error("Error calling sensorEvent callback: %s" % utils.e2str(e))


    def _sendEventWrapper(self, type, id, data, deviceAttributes=None):

        if type == 'sensor':
            sensorId,sensorType = id.split('-')
            if sensorType == '1': sensorType = 'temperature'
            if sensorType == '2': sensorType = 'humidity'

        # phew...

        config = None
        device = '%s-%s' % (type,id)
        for key in self.devices:

            _config = self.devices[key]
            configClass = _config.get('class')
            configType = _config.get('type')

            if type == 'sensor' and configClass == 'sensor':
                configId = None
                configType = _config.get('type')
                configParams = _config.get('parameters')
                if configParams: configId = str(configParams.get('id'))
                if sensorId == configId and sensorType == configType:
                    config = _config
                    device = key
                    break

            if type == 'device' and configClass == 'command':
                configId = _config.get('id')
                if id == configId:
                    config = _config
                    device = key
                    break
                    
        if not deviceAttributes:
            deviceAttributes = {}

        if config:
            if config.get('suppress'):
                log.debug('Config says suppress event: %s' % device)
                return
            if config.get('name'):
                deviceAttributes['name'] = config.get('name')
            if config.get('location'):
                deviceAttributes['location'] = config.get('location')
            # todo: infer these from telldus types instead (done for sensor, todo for device)
            if not deviceAttributes.get('type') and config.get('type'):
                deviceAttributes['type'] = config.get('type')
            if not deviceAttributes.get('type') and type == 'device':
                deviceAttributes['type'] = 'lamp'
        elif self.suppressUnconfigured:
            return

        deviceAttributes['device'] = device

        self.sendEvent('change', data, deviceAttributes)

    def openTelldus(self):

        log.info('Open telldus start')

        td.init( defaultMethods = td.TELLSTICK_TURNON | td.TELLSTICK_TURNOFF | td.TELLSTICK_BELL | td.TELLSTICK_TOGGLE | td.TELLSTICK_DIM | td.TELLSTICK_LEARN )
        #td.debug = True

        log.info('Registering device event handler')
        self.deviceCallbackId = td.registerDeviceEvent(self.deviceEventCallback)

        log.info('Registering sensor event handler')
        self.sensorCallbackId = td.registerSensorEvent(self.sensorEventCallback)
        #td.registerRawDeviceEvent(...) # if we want to support ALL recvd signals. noisy!

        log.info('Open telldus end')

    def closeTelldus(self):

        log.info('Close telldus start')

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

        log.info('Close telldus end')

    def parseDeviceConfig(self):
        data = self.config.data('devices')
        if not data: data = []
        return data

    def sendStartupEvents(self):
        for deviceId in self.devices:
            log.info('send start ev: %s' % deviceId)
            data = self.devices[deviceId]
            if data.get('class') == 'sensor':
                type = 'sensor'
            else:
                type = 'device'
            id = int(data.get('id'))
            if type == 'device':
                self.deviceEventCallback(id, td.TELLSTICK_TURNOFF, 0, 1, True)
            elif type == 'sensor':
                dataType = int(tmp.pop(0))
                self.sensorEventCallback('', '', id, dataType, 0, time.time(), 0, True)

    def writeTellstickConf(self):
        log.info('Writing tellstick.conf')
        text = tellconf.fromServiceConfig(self.config.data())
        tellconf.write(text)

    def restartTelldus(self):
        try:
            log.info('Restart telldusd start')
            proc = subprocess.Popen(['/etc/init.d/telldusd', 'restart'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            ec = proc.wait()
            if ec != 0:
                raise Exception('Failed to restart telldusd:\n%s\n%s' % (out,err))
            log.info('Restart telldusd end')
        except:
            log.error('Restart telldusd failed')

    # todo: move to tellconf
    def readTellstickConf(self):
        f = '/etc/tellstick.conf'
        fp = open(f,'r')
        text = fp.read()
        fp.close()
        return text.strip()
