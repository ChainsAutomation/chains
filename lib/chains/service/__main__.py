#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function

# ALL THIS IS LIFTED DIRECTLY FROM runservice.py

import signal
import os
from chains.service import process
from chains import service
from chains.common import log, utils

from .runservice import signalHandler, parseConfigParam

serviceObject = None

serviceConfig = parseConfigParam()
serviceId = serviceConfig.get('id')

log.setFileName('service-%s-%s' % (serviceConfig.get('name'), serviceId))
if serviceConfig.get('loglevel'):
    log.setLevel(serviceConfig.get('loglevel'))

process.setPid(serviceId, os.getpid())

try:
    serviceObject = service.factory(serviceConfig)

    signal.signal(signal.SIGTERM, signalHandler)  # $ kill <pid>
    signal.signal(signal.SIGINT, signalHandler)  # Ctrl-C

    serviceObject.start(block=True)
except Exception as e:
    log.error('Service crashed: %s' % serviceId)
    log.error(utils.e2str(e))
