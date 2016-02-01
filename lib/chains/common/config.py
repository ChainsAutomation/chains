import os as _os
import yaml as _yaml
import types

class BaseConfig:

    def __init__(self, file=None, data=None):
        self._data = {}
        self._loaded = False
        self._defaultSection = 'main'
        self._file = file
        if data:
            self._data = data
            self._loaded = True
        elif self._file and _os.path.exists(self._file):
            self.load(self._file)
            self._loaded = True

    def data(self, section=None):
        return self._getDataForPath(section)

    def has(self, key, section=None):
        if not section:
            section = self._defaultSection
        prefix = key.split('.')[:-1]
        prefix.insert(0, section)
        prefix = '.'.join(prefix)
        last = key.split('.')[-1:][0]
        data = self._getDataForPath(prefix)
        try:
            if data and data.has_key(last):
                return True
        except TypeError:
            pass
        return False

    def get(self, key, section=None):
        if not section:
            section = self._defaultSection
        return self._getDataForPath(section + '.' + key)

    def getInt(self, key, section=None):
        val = self.get(key, section)
        try: return int(val)
        except: return 0

    def getBool(self, key, section=None):
        val = self.get(key, section)
        if val in [True,'True','true',1,'1','yes','y']:
            return True
        else:
            return False

    def set(self, key, value, section=None):
        if not section:
            section = self._defaultSection
        prefix = key.split('.')[:-1]
        prefix.insert(0, section)
        last = key.split('.')[-1:][0]
        data = self._data
        for key in prefix:
            if not data.has_key(key) or type(data.get(key)) != types.DictType:
                data[key] = {}
            data = data[key]
        data[last] = value

    def save(self):
        text = _yaml.dump(self._data, default_flow_style=False, width=1000)
        fp = open(self._file, 'w')
        fp.write(text)
        fp.close()

    def load(self, path):
        if not _os.path.exists(path):
            return
        fp = open(path, 'r')
        text = fp.read()
        fp.close()
        conf = _yaml.load(text) 
        self._data = conf

    def _getDataForPath(self, path):
        _data = self._data
        if path:
            for key in path.split('.'):
                try:
                    _data = _data.get(key)
                except TypeError:
                    return None
                except AttributeError:
                    return None
        return _data



class CoreConfig(BaseConfig):

    def __init__(self, file=None):
        if not file:
            file = '/etc/chains/chains.yml'
        BaseConfig.__init__(self, file=file)
        if self._loaded:
            return
        if not self._data.has_key('main'):
            self.makeDefaultConfig()
            self._loaded = True

    def makeDefaultConfig(self):

        dir = _os.path.dirname(self._file)
        if not _os.path.exists(dir):
            _os.makedirs(dir)

        isMaster = False
        if os.environ.get('CHAINS_MASTER') and os.environ.get('CHAINS_MASTER') != '0':
            isMaster = True

        self._data = {
            'main': {
                'confdir':    '/etc/chains',
                'datadir':    '/srv/chains/data',
                'bindir':     '/srv/chains/bin',
                'logdir':     '/var/log/chains',
                'sharedir':   '/srv/chains/share',
                'rundir':     '/var/run/chains',
                'libdir':     '/srv/chains/lib/chains',
                'rulesdir':   '/etc/chains',
                'loglevel':   'warn',
                'heartbeat':  5,
            },
            'manager': {
                'id':         '{hostname}'
            }
        }

        if isMaster:
            self._data['reactor']      = { 'id': 'chainsmaster' }
            self._data['orchestrator'] = { 'id': 'main' }

        self.save()

    def getLogFile(self, daemonType):
        if not _os.path.exists(self.get('logdir')):
            _os.makedirs(self.get('logdir'))
        return '%s/%s.log' % (self.get('logdir'), daemonType)

    def getPidFile(self, daemonType):
        if not _os.path.exists(self.get('rundir')):
            _os.makedirs(self.get('rundir'))
        return '%s/%s.pid' % (self.get('rundir'), daemonType)


class ConnectionConfig(BaseConfig):
    def __init__(self):
        BaseConfig.__init__(self, '/etc/chains/amqp.yml')

