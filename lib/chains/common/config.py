import ConfigParser as _ConfigParser
import os as _os

class BaseConfig:
    '''
    Base class for config objects

    Should not be used by itself but rather extended
    to create a config class for a specific thing
    (like CoreConfig for /etc/chains/chains.conf
    and DeviceConfig for devices).
    '''

    def __init__(self, paths):
        self._data = {}                   # Loaded config data
        self._loaded = False              # True when loaded
        self._defaultSection = 'main'     # Default [section] in file
        self._paths = paths               # Config files to try when loading

    def data(self, section=None):
        '''
        Return full config data (if not section param given),
        or data for a specific section (if section param given).
        '''
        self._load()
        if section:
            try:
                return self._data[section]
            except KeyError:
                return None
        else:
            return self._data

    def has(self, key, section=None):
        if not section:
            section = self._defaultSection
        data = self.data()
        if data.has_key(section) and data[section].has_key(key):
            return True
        return False

    def get(self, key, section=None):
        '''
        Return configured value for a key in a section
        (or default section if none given).
        '''
        if not section:
            section = self._defaultSection
        data = self.data()
        try:
            return data[section][key]
        except KeyError:
            return None

    def getInt(self, key, section=None):
        '''
        As get() but return value as an integer.
        '''
        val = self.get(key, section)
        try: return int(val)
        except: return 0

    def getBool(self, key, section=None):
        '''
        As get() but return value as a boolean.
        '''
        val = self.get(key, section)
        if val in [True,'True','true',1,'1','yes','y']:
            return True
        else:
            return False

    def reload(self):
        self._data = {}
        self._loaded = False
        self._load()

    def _load(self):
        '''
        If not already loaded, check each path and
        load the first file that exists.
        '''
        if not self._loaded:
            if not self._paths:
                raise Exception('No config file set')
            for f in self._paths:
                if _os.path.exists(f):
                    self._loadFile(f, self._data)
                    break
        self._loaded = True

    def _loadFile(self, f, data, sections=None, backwdOverride=True):
        '''
        Load a config file from [f] and put results in [data] dict.

        If [sections] is set, load only those sections from file,
        if not load all sections.

        If backwdOverride is True (default) then only overwrite
        those keys in config that are not already set.

        This means the function can be called for f.ex. device config first,
        then for device class config, then for default device config, and
        stuff will be overridden as expected.
        '''
        if not _os.path.exists(f):
            return False
        cp = _ConfigParser.ConfigParser()
        cp.read(f)
        if not sections:
            sections = cp.sections()
        for sect in sections:
            for k in cp.options(sect):
                if not data.has_key(sect):
                    data[sect] = {}
                if not data[sect].has_key(k) or not backwdOverride:
                    data[sect][k] = cp.get(sect, k)
        return True


class CoreConfig(BaseConfig):
    '''
    Config class for /etc/chains/chains.conf
    '''

    def __init__(self):
        BaseConfig.__init__(self, [
            '/etc/chains/chains.conf'
        ])

    def _load(self):
        if self._loaded:
            return
        BaseConfig._load(self)
        if not self._data.has_key('main'):
            path = self._paths[0]
            self.makeDefaultConfig(path)
            self._loadFile(path, self._data)
            self._loaded = True

    def makeDefaultConfig(self, path):

        dir = _os.path.dirname(path)
        if not _os.path.exists(dir):
            _os.makedirs(dir)

        with open(path, 'w') as file:

            c = _ConfigParser.ConfigParser()
            c.add_section('main')
            c.add_section('manager')
            c.set('main', 'confdir', '/etc/chains')
            c.set('main', 'datadir', '/srv/chains/data')
            c.set('main', 'bindir', '/srv/chains/bin')
            c.set('main', 'logdir', '/var/log/chains')
            c.set('main', 'sharedir', '/srv/chains/share')
            c.set('main', 'rundir', '/var/run/chains')
            c.set('main', 'libdir', '/srv/chains/lib/chains')
            c.set('main', 'rulesdir', '/etc/chains')
            c.set('main', 'loglevel', 'warn')
            c.set('main', 'heartbeat', '5')
            c.set('manager', 'id', '{hostname}')

            c.write(file)


class ConnectionConfig(BaseConfig):
    def __init__(self):
        BaseConfig.__init__(self, [
            '/etc/chains/amqp.conf'
        ])


_core = CoreConfig()

def data(*args, **kw):
    return _core.data(*args, **kw)
def has(*args, **kw):
    return _core.has(*args, **kw)
def get(*args, **kw):
    return _core.get(*args, **kw)
def getInt(*args, **kw):
    return _core.getInt(*args, **kw)
def getBool(*args, **kw):
    return _core.getBool(*args, **kw)


def getLogFile(daemonType):
    if not _os.path.exists(get('logdir')):
        _os.makedirs(get('logdir'))
    return '%s/%s.log' % (get('logdir'), daemonType)

def getPidFile(daemonType):
    if not _os.path.exists(get('rundir')):
        _os.makedirs(get('rundir'))
    return '%s/%s.pid' % (get('rundir'), daemonType)

"""
def getLogFile(daemonType, daemonId):
    if not _os.path.exists(get('logdir')):
        _os.makedirs(dir)
    return '%s/%s-%s.log' % (get('logdir'), daemonType, daemonId)
def getPidFile(daemonType, daemonId):
    if not _os.path.exists(get('rundir')):
        _os.makedirs(get('rundir'))
    return '%s/%s-%s.pid' % (get('rundir'), daemonType, daemonId)
"""

