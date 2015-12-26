#!/usr/bin/env python

### ALL THIS IS LIFTED DIRECTLY FROM runservice.py

import sys, signal, os, json
from chains.service import process
from chains.service import config # as serviceConfig
from chains import service
from chains.common import log, utils
#from chains.common import config as globalConfig

from .runservice import signalHandler, parseConfigParam, checkNotRunning

serviceObject = None

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
