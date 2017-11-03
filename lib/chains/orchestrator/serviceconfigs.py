from __future__ import absolute_import
from chains.common import config, utils, log
from chains.service import config as serviceConfig
import six.moves.configparser, os, uuid


class ServiceConfigs():

    def __init__(self):

        coreConfig = config.CoreConfig()
        self.configDir = coreConfig.get('confdir')
        self.libDir = coreConfig.get('libdir')
        self.data = {}

        for path in self._listServiceConfigs():
            self._loadServiceConfig(path)

    def getConfig(self, id):
        return self.data.get(id)

    def getId(self, value):

        # serviceId
        serviceConfig = self.data.get(value)
        if serviceConfig:
            return value

        # managerId.serviceName
        tmp = value.split('.')
        if len(tmp) == 2:
            managerId, serviceName = tmp
            for serviceId in self.data:
                serviceConfig = self.data[serviceId]
                if serviceConfig['main'].get('manager') != managerId:
                    continue
                if serviceConfig['main'].get('name') != serviceName:
                    continue
                return serviceId

        # serviceName
        serviceName = value
        items = []
        for serviceId in self.data:
            serviceConfig = self.data[serviceId]
            if serviceConfig.get('main').get('name') == serviceName:
                items.append(serviceConfig)
        if len(items) == 1:
            serviceConfig = items[0]
            return serviceConfig['main'].get('id')

        # not found
        raise Exception('No such service: %s' % value)


    def _listServiceConfigs(self):
        dir = '%s/services' % self.configDir
        names = {}
        for file in os.listdir(dir):
            tmp = file.split('.')
            ext = tmp.pop()
            name = '.'.join(tmp)
            if ext != 'conf' and ext != 'yml':
                continue
            if name in names and ext != 'yml':
                continue
            names[name] = dir + '/' + file
        return list(names.values())

    def _loadServiceConfig(self, path):

        instanceConfig = self._readConfigFile(path)

        if not instanceConfig:
            return

        instanceData = instanceConfig.data()
        classDir = '%s/config/service-classes' % self.libDir
        classFile = '%s/%s.yml' % (classDir, instanceData['main']['class'])
        classConfig = self._readConfigFile(classFile)
        classData = classConfig.data()
        hasChanges = False

        if not classData:
            return

        if not instanceData['main'].get('id'):
            id = uuid.uuid4().hex
            instanceData['main']['id'] = id
            instanceConfig.set('id', id)
            hasChanges = True

        if not instanceData['main'].get('name'):
            name = instanceData['main']['class'].lower()
            instanceData['main']['name'] = name
            instanceConfig.set('name', name)
            hasChanges = True

        if not instanceData['main'].get('manager'):
            manager = 'master'
            instanceData['main']['manager'] = manager
            instanceConfig.set('manager', manager)
            hasChanges = True

        if hasChanges:
            instanceConfig.save()

        data = self._mergeDictionaries(classData, instanceData)

        self.data[ data['main']['id'] ] = data

    def _readConfigFile(self, path):
        try:
            return config.BaseConfig(path)
        except Exception as e:
            log.error("Error loading config: %s, because: %s" % (path, utils.e2str(e)))
            return None

    def _mergeDictionaries(self, dict1, dict2, result=None):
        if not result:
            result = {}
        for k in set(dict1.keys()).union(list(dict2.keys())):
            if k in dict1 and k in dict2:
                if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                    result[k] = self._mergeDictionaries(dict1[k], dict2[k])
                else:
                    # If one of the values is not a dict, you can't continue merging it.
                    # Value from second dict overrides one in first and we move on.
                    result[k] = dict2[k]
            elif k in dict1:
                result[k] = dict1[k]
            else:
                result[k] = dict2[k]
        return result


if __name__ == '__main__':
    sc = ServiceConfigs()
    print sc.data.keys()
