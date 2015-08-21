from chains.common import ChainsException, ParameterException, NoSuchServiceException
import chains.common.config as _config
#from chains.common.config import BaseConfig
import os

class ServiceConfig(_config.BaseConfig):

    def __init__(self, data=None):
        _config.BaseConfig.__init__(self, None)
        if data:
            self._data = data

    def _load(self): 
        return
        '''
        OUTDATED (slightly)

        Get service config

        These files are loaded:
            services-enabled/<serviceId>.conf         which overrides:
            services/<serviceClass>.conf              which overrides:
            [service_*] sections in chains.conf

        These values are set dynamically:
            config[main][id] = <serviceId>
            config[main][enabled] = True if in services-enabled, False if in services-available
        '''
        if not serviceId:
            raise ParameterException('Missing serviceId')
        f = getInstanceConfigFile(serviceId)
        self._data = {'main': {'enabled': True}}
        # Load service instance config
        if not self._loadFile(f, self._data):
            f = getAvailableConfigFile(serviceId)
            self._data['main']['enabled'] = False
            if not self._loadFile(f, self._data):
                raise ConfigNotFoundException('No config for: %s' % serviceId)
        # Load service class config
        if self._data.has_key('main') and self._data['main'].has_key('class'):
            self._loadFile(getClassConfigFile(self._data['main']['class']), self._data)
        ''' bah.. this crap is not in use?
        # Load service defaults config
        etcConf = _config.data()
        for etcSection in etcConf:
            if etcSection[:7] == 'service_':
                realSection = etcSection[7:]
                if not self._data.has_key(realSection):
                    self._data[realSection] = {}
                for k in etcConf[etcSection]:
                    if not self._data[realSection].has_key(k):
                        self._data[realSection][k] = etcConf[etcSection][k]
        '''
        # ID and UUID
        #self._data['main']['id']   = serviceId
        #self._data['main']['uuid'] = ensureUuid(self.serviceId) 

    def getDataDir(self):
        return getDataPath(self.get('id'))

# Will not work anymore? Remove

def data(serviceId, section=None):
    conf = ServiceConfig(serviceId)
    return conf.data(section)
def has(serviceId, key, section=None):
    conf = ServiceConfig(serviceId)
    return conf.has(key, section)
def get(serviceId, key, section=None):
    conf = ServiceConfig(serviceId)
    return conf.get(key, section)
def getInt(serviceId, key, section=None):
    conf = ServiceConfig(serviceId)
    return conf.getInt(key, section)
def getBool(serviceId, key, section=None):
    conf = ServiceConfig(serviceId)
    return conf.getBool(key, section)

# ======================================
# Paths
# ======================================

"""
def getInstanceConfigFile(serviceId):
    ''' Get path to service instance config dir '''
    path = '%s/services' % _config.get('confdir')
    if not os.path.exists(path):
        os.makedirs(path)
    return '%s/%s.conf' % (path, serviceId)

def getInstanceConfigDir():
    ''' Get path to service instance config dir '''
    path = '%s/services' % _config.get('confdir')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def getServiceIdList():
    ret = []
    dir = getInstanceConfigDir()
    for file in os.listdir(dir):
        if file.split('.')[-1:][0] != 'conf':
            continue
        serviceId = '.'.join(file.split('.')[:-1])
        if serviceId == serviceId.lower():
            ret.append(serviceId)
    ret.sort()
    return ret

def getEnabledConfigDir():
    '''Get path to services-enabled dir'''
    return _getConfigPath(None, True)

def getAvailableConfigDir():
    '''Get path to services-available dir'''
    return _getConfigPath(None, False)

def getEnabledConfigFile(serviceId):
    '''Get path to an enabled service's config file'''
    return _getConfigPath(serviceId, True)

def getAvailableConfigFile(serviceId):
    '''Get path to an available service's config file'''
    return _getConfigPath(serviceId, False)
"""

"""
def getClassConfigDir():
    '''Get path services config dir'''
    return _getClassConfigPath()

def getClassConfigFile(serviceClass):
    '''Get path to a service class' config file'''
    return _getClassConfigPath(serviceClass)
"""

def getLogDir():
    '''Get path to logdir for services'''
    return _getLogPath(serviceId, False)

def getLogFile(serviceId):
    '''Get path to a service's logfile'''
    return _getLogPath(serviceId, True)

def getDataPath(serviceId):
    '''Get path to a service's data dir'''
    dir = '%s/services/%s' % (_config.get('datadir'), serviceId)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def getSharePath(serviceClass):
    '''Get path to a service's share dir'''
    dir = '%s/services/%s' % (_config.get('sharedir'), serviceClass)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def getUuidFile(serviceId):
    dir = '%s/service-uuids' % _config.get('datadir')
    if not os.path.exists(dir):
        os.makedirs(dir)
    return '%s/%s' % (dir, serviceId)

def ensureUuid(serviceId):
    file = getUuidFile(serviceId)
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
def _getConfigPath(serviceId=None, isEnabled=True):
    '''Get path to config dir or file for enabled or available service(s)'''
    entxt = 'enabled'
    if not isEnabled:
        entxt = 'available'
    f = '%s/services_%s' % (_config.get('confdir'), entxt)
    if not os.path.exists(f):
        os.makedirs(f)
    if serviceId:
        f = '%s/%s.conf' % (f, serviceId)
    return f
"""

def _getClassConfigPath(serviceClass=None):
    '''Get path to config dir or file for service class(es)'''
    f = '%s/config/service-classes' % _config.get('libdir')
    if not os.path.exists(f):
        os.makedirs(f)
    if serviceClass:
        f = '%s/%s.conf' % (f, serviceClass)
    return f

def _getLogPath(serviceId, filename=None):
    '''Get path to log dir or file for service(s)'''
    dir = '%s/services' % _config.get('logdir')
    if filename: dir += '/' + serviceId
    if not os.path.exists(dir):
        os.makedirs(dir)
    if not filename: filename = '%s.log' % serviceId
    return '%s/%s' % (dir, filename)

# ======================================
# Enable/disable/list
# ======================================

"""
def getEnabledServiceList():
    '''Get a list of enabled service ids'''
    return _getServiceList(True)

def getAvailableServiceList():
    '''Get a list of available service ids'''
    return _getServiceList(False)

def enableService(serviceId):
    '''Enable a service by adding symlink between file in services-available and services-enabled'''
    if not serviceId:
        raise ParameterException('Missing serviceId')
    src = getAvailableConfigFile(serviceId)
    dst = getEnabledConfigFile(serviceId)
    if not os.path.exists(src):
        raise NoSuchServiceException(serviceId)
    if os.path.exists(dst):
        raise ServiceAlreadyEnabledException(serviceId)
    os.symlink(src, dst)

def disableService(serviceId):
    '''Disable a service by removing symlink between file in services-available and services-enabled'''
    if not serviceId:
        raise ParameterException('Missing serviceId')
    src = getAvailableConfigFile(serviceId)
    dst = getEnabledConfigFile(serviceId)
    if not os.path.exists(src):
        raise NoSuchServiceException(serviceId)
    if not os.path.exists(dst):
        raise ServiceAlreadyDisabledException(serviceId)
    os.unlink(dst)

def _getServiceList(isEnabled):
    '''Get list of service ids in services-available or services-enabled'''
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

class ServiceConfigNotFoundException(ChainsException):
    pass

class ServiceAlreadyEnabledException(ChainsException):
    def __init__(self, serviceId):
        ChainsException.__init__(self, 'Service already enabled: %s' % serviceId)
        self.serviceId = serviceId

class ServiceAlreadyDisabledException(ChainsException):
    def __init__(self, serviceId):
        ChainsException.__init__(self, 'Service already disabled: %s' % serviceId)
        self.serviceId = serviceId

