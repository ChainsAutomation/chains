from chains.common import ChainsException, ParameterException, NoSuchDeviceException
import chains.common.config as _config
#from chains.common.config import BaseConfig
import os

class DeviceConfig(_config.BaseConfig):

    def __init__(self, data=None):
        _config.BaseConfig.__init__(self, None)
        if data:
            self._data = data

    def _load(self): 
        return
        '''
        OUTDATED (slightly)

        Get device config

        These files are loaded:
            devices-enabled/<deviceId>.conf         which overrides:
            devices/<deviceClass>.conf              which overrides:
            [device_*] sections in chains.conf

        These values are set dynamically:
            config[main][id] = <deviceId>
            config[main][enabled] = True if in devices-enabled, False if in devices-available
        '''
        if not deviceId:
            raise ParameterException('Missing deviceId')
        f = getInstanceConfigFile(deviceId)
        self._data = {'main': {'enabled': True}}
        # Load device instance config
        if not self._loadFile(f, self._data):
            f = getAvailableConfigFile(deviceId)
            self._data['main']['enabled'] = False
            if not self._loadFile(f, self._data):
                raise ConfigNotFoundException('No config for: %s' % deviceId)
        # Load device class config
        if self._data.has_key('main') and self._data['main'].has_key('class'):
            self._loadFile(getClassConfigFile(self._data['main']['class']), self._data)
        ''' bah.. this crap is not in use?
        # Load device defaults config
        etcConf = _config.data()
        for etcSection in etcConf:
            if etcSection[:7] == 'device_':
                realSection = etcSection[7:]
                if not self._data.has_key(realSection):
                    self._data[realSection] = {}
                for k in etcConf[etcSection]:
                    if not self._data[realSection].has_key(k):
                        self._data[realSection][k] = etcConf[etcSection][k]
        '''
        # ID and UUID
        #self._data['main']['id']   = deviceId
        #self._data['main']['uuid'] = ensureUuid(self.deviceId) 

    def getDataDir(self):
        return getDataPath(self.get('id'))

# Will not work anymore? Remove

def data(deviceId, section=None):
    conf = DeviceConfig(deviceId)
    return conf.data(section)
def has(deviceId, key, section=None):
    conf = DeviceConfig(deviceId)
    return conf.has(key, section)
def get(deviceId, key, section=None):
    conf = DeviceConfig(deviceId)
    return conf.get(key, section)
def getInt(deviceId, key, section=None):
    conf = DeviceConfig(deviceId)
    return conf.getInt(key, section)
def getBool(deviceId, key, section=None):
    conf = DeviceConfig(deviceId)
    return conf.getBool(key, section)

# ======================================
# Paths
# ======================================

"""
def getInstanceConfigFile(deviceId):
    ''' Get path to device instance config dir '''
    path = '%s/devices' % _config.get('confdir')
    if not os.path.exists(path):
        os.makedirs(path)
    return '%s/%s.conf' % (path, deviceId)

def getInstanceConfigDir():
    ''' Get path to device instance config dir '''
    path = '%s/devices' % _config.get('confdir')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def getDeviceIdList():
    ret = []
    dir = getInstanceConfigDir()
    for file in os.listdir(dir):
        if file.split('.')[-1:][0] != 'conf':
            continue
        deviceId = '.'.join(file.split('.')[:-1])
        if deviceId == deviceId.lower():
            ret.append(deviceId)
    ret.sort()
    return ret

def getEnabledConfigDir():
    '''Get path to devices-enabled dir'''
    return _getConfigPath(None, True)

def getAvailableConfigDir():
    '''Get path to devices-available dir'''
    return _getConfigPath(None, False)

def getEnabledConfigFile(deviceId):
    '''Get path to an enabled device's config file'''
    return _getConfigPath(deviceId, True)

def getAvailableConfigFile(deviceId):
    '''Get path to an available device's config file'''
    return _getConfigPath(deviceId, False)
"""

"""
def getClassConfigDir():
    '''Get path devices config dir'''
    return _getClassConfigPath()

def getClassConfigFile(deviceClass):
    '''Get path to a device class' config file'''
    return _getClassConfigPath(deviceClass)
"""

def getLogDir():
    '''Get path to logdir for devices'''
    return _getLogPath(deviceId, False)

def getLogFile(deviceId):
    '''Get path to a device's logfile'''
    return _getLogPath(deviceId, True)

def getDataPath(deviceId):
    '''Get path to a device's data dir'''
    dir = '%s/devices/%s' % (_config.get('datadir'), deviceId)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def getSharePath(deviceClass):
    '''Get path to a device's share dir'''
    dir = '%s/devices/%s' % (_config.get('sharedir'), deviceClass)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def getUuidFile(deviceId):
    dir = '%s/device-uuids' % _config.get('datadir')
    if not os.path.exists(dir):
        os.makedirs(dir)
    return '%s/%s' % (dir, deviceId)

def ensureUuid(deviceId):
    file = getUuidFile(deviceId)
    uuid = None
    if os.path.exists(file):
        with open(file, 'r') as fp:
            uuid = fp.read()
    if uuid:
        return uuid
    uuid = uuid.uuid4().hex
    with open(file, 'w') as fp:
        fp.write(uuid)
    return uuid


"""
def _getConfigPath(deviceId=None, isEnabled=True):
    '''Get path to config dir or file for enabled or available device(s)'''
    entxt = 'enabled'
    if not isEnabled:
        entxt = 'available'
    f = '%s/devices_%s' % (_config.get('confdir'), entxt)
    if not os.path.exists(f):
        os.makedirs(f)
    if deviceId:
        f = '%s/%s.conf' % (f, deviceId)
    return f
"""

def _getClassConfigPath(deviceClass=None):
    '''Get path to config dir or file for device class(es)'''
    f = '%s/config/device-classes' % _config.get('libdir')
    if not os.path.exists(f):
        os.makedirs(f)
    if deviceClass:
        f = '%s/%s.conf' % (f, deviceClass)
    return f

def _getLogPath(deviceId, filename=None):
    '''Get path to log dir or file for device(s)'''
    dir = '%s/devices' % _config.get('logdir')
    if filename: dir += '/' + deviceId
    if not os.path.exists(dir):
        os.makedirs(dir)
    if not filename: filename = '%s.log' % deviceId
    return '%s/%s' % (dir, filename)

# ======================================
# Enable/disable/list
# ======================================

"""
def getEnabledDeviceList():
    '''Get a list of enabled device ids'''
    return _getDeviceList(True)

def getAvailableDeviceList():
    '''Get a list of available device ids'''
    return _getDeviceList(False)

def enableDevice(deviceId):
    '''Enable a device by adding symlink between file in devices-available and devices-enabled'''
    if not deviceId:
        raise ParameterException('Missing deviceId')
    src = getAvailableConfigFile(deviceId)
    dst = getEnabledConfigFile(deviceId)
    if not os.path.exists(src):
        raise NoSuchDeviceException(deviceId)
    if os.path.exists(dst):
        raise DeviceAlreadyEnabledException(deviceId)
    os.symlink(src, dst)

def disableDevice(deviceId):
    '''Disable a device by removing symlink between file in devices-available and devices-enabled'''
    if not deviceId:
        raise ParameterException('Missing deviceId')
    src = getAvailableConfigFile(deviceId)
    dst = getEnabledConfigFile(deviceId)
    if not os.path.exists(src):
        raise NoSuchDeviceException(deviceId)
    if not os.path.exists(dst):
        raise DeviceAlreadyDisabledException(deviceId)
    os.unlink(dst)

def _getDeviceList(isEnabled):
    '''Get list of device ids in devices-available or devices-enabled'''
    ret = []
    if isEnabled:
        p = getEnabledConfigDir()
    else:
        p = getAvailableConfigDir()
    for f in os.listdir(p):
        if f.split('.')[-1:][0] != 'conf':
            continue
        d = '.'.join(f.split('.')[:-1])
        if d == d.lower():
            ret.append(d)
    ret.sort()
    return ret
"""

# ======================================
# Exceptions
# ======================================

class DeviceConfigNotFoundException(ChainsException):
    pass

class DeviceAlreadyEnabledException(ChainsException):
    def __init__(self, deviceId):
        ChainsException.__init__(self, 'Device already enabled: %s' % deviceId)
        self.deviceId = deviceId

class DeviceAlreadyDisabledException(ChainsException):
    def __init__(self, deviceId):
        ChainsException.__init__(self, 'Device already disabled: %s' % deviceId)
        self.deviceId = deviceId

