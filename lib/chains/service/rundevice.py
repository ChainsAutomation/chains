#!/usr/bin/env python

import sys, signal, os, json
from chains.service import process
from chains.service import config # as serviceConfig
from chains import service
from chains.common import log, utils
#from chains.common import config as globalConfig

serviceObject = None

def signalHandler(signal, frame):
    if serviceObject:
        serviceObject.shutdown()
    sys.exit(0)

def parseConfigParam():
    if len(sys.argv) < 2:
        print 'usage: %s {..service-config-json..}' % sys.argv[0]
        sys.exit(1)
    serviceConfigData = json.loads(sys.argv[1])
    if not serviceConfigData:
        raise Exception('Invalid service-config-json: %s' % sys.argv[1])
    serviceConfig = config.ServiceConfig(data=serviceConfigData)
    return serviceConfig

def checkNotRunning(serviceId):
    pid = process.isRunning(serviceId)
    if pid:
        print "Service %s is already running on pid %s" % (serviceId, pid)
        sys.exit(100)

if __name__ == '__main__':

    serviceConfig = parseConfigParam()
    serviceId     = serviceConfig.get('id')

    log.setFileName('service-%s-%s' % (serviceConfig.get('name'), serviceId))
    if serviceConfig.get('loglevel'):
        log.setLevel(serviceConfig.get('loglevel'))

    #checkNotRunning(serviceId)
    process.setPid(serviceId, os.getpid())

    try:
        serviceObject = service.factory(serviceConfig)

        signal.signal(signal.SIGTERM, signalHandler) # $ kill <pid>
        signal.signal(signal.SIGINT, signalHandler)  # Ctrl-C

        serviceObject.start(block=True)
    except Exception, e:
        log.error('Service crashed: %s' % serviceId)
        log.error(utils.e2str(e))
