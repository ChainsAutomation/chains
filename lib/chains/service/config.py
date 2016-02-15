from __future__ import absolute_import
from __future__ import print_function
from chains.common import ChainsException, ParameterException, NoSuchServiceException
import chains.common.config as _config
import os

class ServiceConfig(_config.BaseConfig):

    def getDataDir(self):
        serviceId = self.get('id')
        dir = '%s/services/%s' % (_config.get('datadir'), serviceId)
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

