from chains.common import log, utils, amqp, config
from chains.device import config as deviceConfig
import time, threading, ConfigParser, os, uuid

class TimeoutThread(threading.Thread):
    '''
    Thread for checking if daemons have timed out.

    Will periodically check last heartbeat time for
    managers, devices, and reactors, and if it is too old,
    the item in question will be set as offline.
    '''

    def __init__(self, orchestrator):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.orchestrator = orchestrator

    def run(self):
        while True:

            # Run thru all types (manager, device, reactor)
            for daemonType in self.orchestrator.data:

                # For each item (f.ex. for each manager)
                for daemonId in self.orchestrator.data[daemonType]:

                    self.handleDaemonItem(daemonType, daemonId)

            # Broadcst heartbeat request, to get fresh heartbeats for next run
            self.orchestrator.sendHeartBeatRequest()

            # Pause interval
            time.sleep(self.orchestrator.timeoutInterval)

    def handleDaemonItem(self, type, id):

        # If item is already offline, do nothing - but (re)start if applicable
        item = self.orchestrator.data[type][id]
        if item['online'] == False:

            if type == 'device':

                if not item.has_key('offlineTimer'):
                    item['offlineTimer'] = time.time()

                if item['main'].get('autostart'):
                    timeSinceOffline = time.time() - item['offlineTimer']
                    if timeSinceOffline > self.orchestrator.startInterval:
                        self.orchestrator.data[type][id]['offlineTimer'] = time.time()
                        try:
                            #self.orchestrator.action_startDevice(id)
                            deviceId, managerId = self.orchestrator.parseDeviceParam(id)
                            if self.orchestrator.isOnline('manager', managerId):
                                log.info('Auto-start device %s after %s secs offline' % (id, timeSinceOffline))
                                self.orchestrator.startDevice(managerId, deviceId)
                            else:
                                log.debug('Do not auto-start device %s since manager %s is offline' % (id,managerId))
                        except Exception, e:
                            log.error('Error trying to autostart device %s: %s' % (id,e))
                    else:
                        log.debug('Do not auto-start device %s since %s secs offline is less than startinterval %s' % (id,timeSinceOffline,self.orchestrator.startInterval))
                else:
                    log.debug('Do not auto-start device %s since autostart not set in config' % (id,))

            return

        # If item is online...
        # Check if existing heartbeat is old, and if so, set to offline
        if not item.has_key('heartbeat'):
            item['heartbeat'] = 0
        else:
            now = time.time()
            if (now-item['heartbeat']) > self.orchestrator.timeout:
                log.info('now %s - hb %s > timeout %s' % (now,item['heartbeat'],self.orchestrator.timeout))
                self.orchestrator.setOffline(type, id)



class Orchestrator(amqp.AmqpDaemon):

    def __init__(self, id):
        log.info('Starting orchestator')
        amqp.AmqpDaemon.__init__(self, 'orchestrator', id)
        self.data = {
            'manager':      {},
            'device':       {},
            'reactor':      {},
            'orchestrator': {}
        }
        self.timeout = 30
        self.timeoutInterval = 5
        self.startInterval = 15
        self.timeoutThread = TimeoutThread(self)
        self.loadDeviceConfigs()

    def run(self):
        self.sendEvent('online', {'value': True})
        self.timeoutThread.start()
        self.listen()
        self.sendEvent('online', {'value': False})

    def getConsumeKeys(self):
        return [
            # actions to orchestrator itself
            '%s%s.%s.*' % (amqp.PREFIX_ORCHESTRATOR, amqp.PREFIX_ACTION, self.id),

            # online/offline/heartbeat events
            '%s%s.*' % (amqp.PREFIX_DEVICE,  amqp.PREFIX_HEARTBEAT_RESPONSE),
            '%s%s.*' % (amqp.PREFIX_MANAGER, amqp.PREFIX_HEARTBEAT_RESPONSE),
            '%s%s.*' % (amqp.PREFIX_REACTOR, amqp.PREFIX_HEARTBEAT_RESPONSE),
        ]

    def prefixToType(self, prefix):
        if prefix == amqp.PREFIX_DEVICE:       return 'device'
        if prefix == amqp.PREFIX_MANAGER:      return 'manager'
        if prefix == amqp.PREFIX_REACTOR:      return 'reactor'
        if prefix == amqp.PREFIX_ORCHESTRATOR: return 'orchestrator'

    def typeToPrefix(self, type):
        return self.getDaemonTypePrefix(type)
        '''
        if type == 'device': return amqp.PREFIX_DEVICE
        if type == 'manager': return amqp.PREFIX_MANAGER
        if type == 'reactor': return amqp.PREFIX_REACTOR
        '''

    def sendHeartBeatRequest(self): #, type, id):
        #topic = '%s.%s' (self.getHeartBeatRequestPrefix(type), id)
        topic = self.getHeartBeatRequestPrefix()
        self.producer.put(topic, amqp.HEARTBEAT_VALUE_REQUEST)

    def onMessage(self, topic, data, correlationId):
        #log.info('MSG: %s = %s' % (topic,data))
        topic = topic.split('.')

        # Heartbeats
        if topic[0][1] == amqp.PREFIX_HEARTBEAT_RESPONSE:
            if data == amqp.HEARTBEAT_VALUE_OFFLINE:
                self.setOffline(self.prefixToType(topic[0][0]), topic[1])
            elif data == amqp.HEARTBEAT_VALUE_ONLINE:
                self.setOnline(self.prefixToType(topic[0][0]), topic[1], force=True)
            elif data == amqp.HEARTBEAT_VALUE_RESPONSE:
                self.setOnline(self.prefixToType(topic[0][0]), topic[1])
            else:
                log.warn('Unknown heartbeat event: %s' % (topic,))

        # Device list responses
        '''
        elif topic[0][1] == amqp.PREFIX_ACTION_RESPONSE and topic[2] == 'getDevices':

            managerId = topic[1]

            # Remove existing devices for the manager
            removeDevices = []
            for deviceId in self.data['device']:
                if not self.data['device'][deviceId].has_key('manager') or self.data['device'][deviceId]['manager'] == managerId:
                    removeDevices.append(deviceId)
            for deviceId in removeDevices:
                del self.data['device'][deviceId]

            # Add devices from manager reply
            for deviceId in data:
                if not self.data['device'].has_key(deviceId):
                    self.data['device'][deviceId] = data[deviceId]
                else:
                    self.data['device'][deviceId]['online'] = data[deviceId]['online']
                self.data['device'][deviceId]['manager'] = managerId
            self.data['manager'][managerId]['devices'] = len(data)

        # Manager reconfigure events - should trigger refresh of device list
        elif topic[0][1] == amqp.PREFIX_EVENT and topic[2] == 'reconfigured':
            newDevices = {}
            for id in self.data['device']:
                if self.data['device'][id]['manager'] == topic[1]:
                    continue
                newDevices[id] = self.data['device'][id]
            self.data['device'] = newDevices
            self.data['manager'][topic[1]]['devices'] = None
            log.info('Ask manager %s for device list since reconfigured' % topic[1])
            self.sendManagerAction(topic[1], 'getDevices')
        '''
            
    def setOnline(self, type, key, force=False):

        if not type or not key:
            log.warn('Ignore attempt to set type=%s id=%s as online' % (type,key))
            return

        # Init dict path if not set
        if not self.data[type].has_key(key):
            self.data[type][key] = {'online': None}
            #if type == 'manager':
            #    self.data[type][key]['devices'] = None

        # If not already online (or force [re-]online)
        # Set online and send online-event
        if self.data[type][key]['online'] != True or force:
            log.info('%s %s changed status to online' % (type, key))
            self.data[type][key]['online'] = True
            '''
            if type == 'manager':
                log.info('Ask manager %s for device list since changed to online' % key)
                self.sendManagerAction(key, 'getDevices')
            '''
            eventTopic = '%s%s.%s.online' % (
                self.typeToPrefix(type),
                amqp.PREFIX_EVENT, 
                key
            )
            event = {'data': {'value': True}, 'key': 'online'}
            if type == 'device':
                event['device'] = key
            else:
                event['host'] = key
            self.producer.put(eventTopic, event)

        # Update last heartbeat time
        self.data[type][key]['heartbeat'] = time.time()

    def setOffline(self, type, key):

        if not type or not key:
            log.warn('Ignore attempt to set type=%s id=%s as offline' % (type,key))
            return

        # Init dict path if not set
        if not self.data[type].has_key(key):
            self.data[type][key] = {'online': None}
            #if type == 'manager':
            #    self.data[type][key]['devices'] = None

        # If not already offline, set offline and send offline event
        if self.data[type][key]['online'] != False:
            log.info('%s %s changed status to offline' % (type, key))
            self.data[type][key]['online'] = False
            self.data[type][key]['offlineTimer'] = time.time()

            eventTopic = '%s%s.%s.online' % (
                self.typeToPrefix(type),
                amqp.PREFIX_EVENT, 
                key
            )
            event = {'data': {'value': False}, 'key': 'online'}
            if type == 'device':
                event['device'] = key
            else:
                event['host'] = key
            self.producer.put(eventTopic, event)

    def isOnline(self, type, key):
        try:
            return self.data[type][key]['online']
        except KeyError:
            return False

    def reloadDeviceConfigs(self):
        self.loadDeviceConfigs(isReload=True)

    def loadDeviceConfigs(self, isReload=False):
        if not isReload or not self.data.get('device'):
            self.data['device'] = {}
        for path in self.getDeviceConfigList():
            self.loadDeviceConfig(path, isReload=isReload)

    def loadDeviceConfig(self, path, isReload=False):

        if isReload:
            log.info('Reload device config: %s' % path)
        else:
            log.info('Load device config: %s' % path)

        instanceConfig    = self.loadConfigFile(path)
        instanceData      = self.configParserToDict(instanceConfig)
        classDir          = '%s/config/device-classes' % config.get('libdir')
        classFile         = '%s/%s.conf' % (classDir, instanceData['main']['class'])
        classConfig       = self.loadConfigFile(classFile)
        classData         = self.configParserToDict(classConfig)
        data              = self.mergeDictionaries(classData, instanceData)

        data['online']    = False
        data['heartbeat'] = 0

        hasChanges = False

        if not instanceData['main'].get('id'):
            id = self.generateUuid()
            instanceData['main']['id'] = id
            instanceConfig.set('main', 'id', id)
            hasChanges = True

        if not instanceData['main'].get('name'):
            name = instanceData['main']['class'].lower()
            instanceData['main']['name'] = name
            instanceConfig.set('main', 'name', name)
            hasChanges = True

        if hasChanges:
            instanceFile = open(path, 'w')
            instanceConfig.write(instanceFile)
            instanceFile.close()

        if isReload and self.data['device'].has_key( data['main']['id'] ):

            old               = self.data['device'][ data['main']['id'] ]
            data['online']    = old.get('online')
            data['heartbeat'] = old.get('heartbeat')

            if not data.get('online'):     data['online'] = False
            if not data.get('heartbeat'):  data['heartbeat'] = 0

        self.data['device'][ data['main']['id'] ] = data

    def loadConfigFile(self, path):
        conf = ConfigParser.ConfigParser()
        conf.read(path)
        return conf

    def configParserToDict(self, conf):
        data = {}
        for section in conf.sections():
            if not data.has_key(section):
                data[section] = {}
            for key in conf.options(section):
                data[section][key] = conf.get(section, key)
        return data

    def mergeDictionaries(self, dict1, dict2, result=None):
        if not result:
            result = {}
        for k in set(dict1.keys()).union(dict2.keys()):
            if k in dict1 and k in dict2:
                if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                    result[k] = self.mergeDictionaries(dict1[k], dict2[k])
                else:
                    # If one of the values is not a dict, you can't continue merging it.
                    # Value from second dict overrides one in first and we move on.
                    result[k] = dict2[k]
            elif k in dict1:
                result[k] = dict1[k]
            else:
                result[k] = dict2[k]
        return result



    def getDeviceConfigList(self):
        ret = []
        dir = '%s/devices' % config.get('confdir')
        for file in os.listdir(dir):
            if file.split('.')[-1:][0] != 'conf':
                continue
            ret.append('%s/%s' % (dir,file))
        ret.sort()
        return ret



    def getDeviceManager(self, deviceId):
        try:
            item = self.data['device'][deviceId]
        except KeyError:
            return None
        else:
            return item['main']['manager']

    def sendManagerAction(self, managerId, action, args=None):
        if not self.isOnline('manager', managerId):
            raise Exception('Manager not online: %s' % managerId)
        amqp.AmqpDaemon.sendManagerAction(self, managerId, action, args)


    def action_getManagers(self):
        return self.data['manager']

    def action_getDevices(self):
        '''
        ret = []
        for deviceId in self.data['device']:
            conf = self.data['device'][deviceId]
            main = conf.get('main')
            ret.append({
                'id':       main.get('id'),
                'class':    main.get('class'),
                'manager':  main.get('manager'),
                'online':   conf.get('online'),
                'hearbeat': conf.get('heartbeat')
            })
        return ret
        '''
        return self.data['device']

    def action_getReactors(self):
        return self.data['reactor']

    '''
    def action_reloadManager(self, managerId):
        self.sendManagerAction(managerId, 'reload')
    '''

    def action_getDeviceConfig(self, device):
        deviceId, managerId = self.parseDeviceParam(device)
        config = self.data['device'][deviceId]
        return config

    def action_reload(self):
        self.reloadDeviceConfigs()


    # ===================================================
    # Manager proxy
    # @todo: use rpc so can get response result?
    # ===================================================

    def action_startDevice(self, device):
        #self.reloadDeviceConfigs()
        deviceId, managerId = self.parseDeviceParam(device)
        self.startDevice(managerId, deviceId)

    def action_stopDevice(self, device):
        deviceId, managerId = self.parseDeviceParam(device)
        self.sendManagerAction(managerId, 'stopDevice', [deviceId])

    def startDevice(self, managerId, deviceId):
        config = self.data['device'][deviceId]
        self.sendManagerAction(managerId, 'startDevice', [config])

    '''
    def action_enableDevice(self, deviceId):
        managerId = self.getDeviceManager(deviceId)
        if not managerId:
            raise Exception('No such device: %s' % deviceId)
        self.sendManagerAction(managerId, 'enableDevice', [deviceId])

    def action_disableDevice(self, deviceId):
        managerId = self.getDeviceManager(deviceId)
        if not managerId:
            raise Exception('No such device: %s' % deviceId)
        self.sendManagerAction(managerId, 'disableDevice', [deviceId])
    '''


    def generateUuid(self):
        return uuid.uuid4().hex

    def parseDeviceParam(self, value):

        # deviceId
        deviceConfig = self.data['device'].get(value)
        if deviceConfig:
            #log.info("parseDeviceParam(1): %s => %s @ %s" % (value, value, deviceConfig['main'].get('manager')))
            return value, deviceConfig['main'].get('manager')

        # managerId.deviceName
        tmp = value.split('.')
        if len(tmp) == 2:
            managerId, deviceName = tmp
            for deviceId in self.data['device']:
                deviceConfig = self.data['device'][deviceId]
                if deviceConfig['main'].get('manager') != managerId:
                    continue
                if deviceConfig['main'].get('name') != deviceName:
                    continue
                #log.info("parseDeviceParam(2): %s => %s @ %s" % (value, deviceId, managerId))
                return deviceId, managerId

        # deviceName
        deviceName = value
        items      = []
        for deviceId in self.data['device']:
            deviceConfig = self.data['device'][deviceId]
            if deviceConfig.get('main').get('name') == deviceName:
                items.append(deviceConfig)
        if len(items) == 1:
            deviceConfig = items[0]
            #log.info("parseDeviceParam(3): %s => %s @ %s" % (value,deviceConfig['main'].get('id'), deviceConfig['main'].get('manager'))) 
            return deviceConfig['main'].get('id'), deviceConfig['main'].get('manager')
        
        # not found
        raise Exception('No such device: %s' % value)



def main(id):
    log.setFileName('orchestrator')
    amqp.runWithSignalHandler(Orchestrator(id))

if __name__ == '__main__':
    main('main')
