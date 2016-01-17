from chains.common import ChainsException, ParameterException, NoSuchServiceException
import chains.common.config as _config
import os

# is this in use at all?

class ServiceConfig(_config.BaseConfig):

    def __init__(self, data=None):
        _config.BaseConfig.__init__(self, None)
        if data:
            self._data = data

    # outdated
    def _load(self): 
        return

    def getDataDir(self):
        serviceId = self.get('id')
        dir = '%s/services/%s' % (_config.get('datadir'), serviceId)
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

