import ConfigParser as _ConfigParser
import os as _os
import yaml as _yaml
import types

class BaseConfig:
    '''
    Base class for config objects

    Should not be used by itself but rather extended
    to create a config class for a specific thing,
    like CoreConfig for /etc/chains/chains.conf
    '''

    def __init__(self, file=None, data=None):
        self._data = {}
        self._loaded = False
        self._defaultSection = 'main'
        self._file = file
        print 'data: %s'%data
        if data:
            self._data = data
            self._loaded = True

    def data(self, section=None, join=True):
        '''
        Return full config data (if not section param given),
        or data for a specific section (if section param given).

        If join=False then keys nested data is returned as dict,
        ie. foo.bar = Moo returns {foo: { bar: Moo }} not {foo.bar: Moo}
        '''
        self._load()
        _data = self._data
        if join:
            for key in _data:
                root = {}
                self._joinKeys(_data[key], root, [])
                _data[key] = root
        if section:
            try:
                return _data[section]
            except KeyError:
                return None
        else:
            return _data
        

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

    def _load(self):
        '''
        Load data from file (if not already loaded)
        '''
        if not self._loaded:
            if self._file and _os.path.exists(self._file):
                self._loadFile(self._file, self._data)
        self._loaded = True

    def _loadFile(self, f, data, sections=None, backwdOverride=True):
        '''
        Load a config file from [f] and put results in [data] dict.

        If [sections] is set, load only those sections from file,
        if not load all sections.

        If backwdOverride is True (default) then only overwrite
        those keys in config that are not already set.

        This means the function can be called for f.ex. service config first,
        then for service class config, then for default service config, and
        stuff will be overridden as expected.

        NB: This override-logic is no longer handled here, and backwdOverride
        and related code can probably be removed. (stian, 2016-01-17)
        '''
        if not _os.path.exists(f):
            return False

        if f[-4:] == '.yml':
            self._loadYaml(f, data, sections, backwdOverride)
        else:
            self._loadIni(f, data, sections, backwdOverride)

    def _loadYaml(self, f, data, sections, backwdOverride):
        fp = open(f, 'r')
        text = fp.read()
        fp.close()
        conf = _yaml.load(text) 
        if not sections:
            sections = conf.keys()
        for sect in sections:
            for k in conf[sect]:
                if not data.has_key(sect):
                    data[sect] = {}
                if not data[sect].has_key(k) or not backwdOverride:
                    data[sect][k] = conf[sect][k]

    def _loadIni(self, f, data, sections, backwdOverride):

        cp = _ConfigParser.ConfigParser()
        cp.read(f)
        if not sections:
            sections = cp.sections()
        for sect in sections:
            for k in cp.options(sect):
                if not data.has_key(sect):
                    data[sect] = {}
                if not data[sect].has_key(k) or not backwdOverride:
                    #data[sect][k] = cp.get(sect, k)
                    self._splitIniKey(data[sect], k, cp.get(sect,k))
        return True

    # These two are needed to handle nested values in .yml and .ini in a unified way

    def _splitIniKey(self, data, key, value):
        parts = key.split('.')
        _data = data
        index = -1
        if len(parts) > 1:
            for i in range(len(parts)-1):
                part = parts[i]
                if not _data.has_key(part):
                    _data[part] = {}
                _data = _data[part]
                index += 1
        part = parts[index+1]
        _data[part] = value

    def _joinKeys(self, data, root, stack):
        if type(data) != types.DictType:
            return
        for key in data:
            stack.append(key)
            if type(data[key]) == types.DictType:
                self._joinKeys(data[key], root, stack)
            else:
                root[ '.'.join(stack) ] = data[key]
            stack.pop()


class CoreConfig(BaseConfig):
    '''
    Config class for /etc/chains/chains.conf
    '''

    def __init__(self):
        BaseConfig.__init__(self, file='/etc/chains/chains.conf')

    def _load(self):
        if self._loaded:
            return
        BaseConfig._load(self)
        if not self._data.has_key('main'):
            self.makeDefaultConfig(self._file)
            self._loadFile(self._file, self._data)
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

    def getLogFile(self, daemonType):
        if not _os.path.exists(get('logdir')):
            _os.makedirs(get('logdir'))
        return '%s/%s.log' % (get('logdir'), daemonType)

    def getPidFile(self, daemonType):
        if not _os.path.exists(get('rundir')):
            _os.makedirs(get('rundir'))
        return '%s/%s.pid' % (get('rundir'), daemonType)


class ConnectionConfig(BaseConfig):
    def __init__(self):
        BaseConfig.__init__(self, '/etc/chains/amqp.conf')



# todo: get rid of this? use CoreConfig explicitly (stian, 2016-01-17)

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

