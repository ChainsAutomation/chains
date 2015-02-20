#!/usr/bin/env python

import sys, signal, os, json
from chains.device import process
from chains.device import config # as deviceConfig
from chains import device
from chains.common import log, utils
#from chains.common import config as globalConfig

deviceObject = None

def signalHandler(signal, frame):
    if deviceObject:
        deviceObject.shutdown()
    sys.exit(0)

def parseConfigParam():
    if len(sys.argv) < 2:
        print 'usage: %s {..device-config-json..}' % sys.argv[0]
        sys.exit(1)
    deviceConfigData = json.loads(sys.argv[1])
    if not deviceConfigData:
        raise Exception('Invalid device-config-json: %s' % sys.argv[1])
    deviceConfig = config.DeviceConfig(data=deviceConfigData)
    return deviceConfig

def checkNotRunning(deviceId):
    pid = process.isRunning(deviceId)
    if pid:
        print "Device %s is already running on pid %s" % (deviceId, pid)
        sys.exit(100)

if __name__ == '__main__':

    deviceConfig = parseConfigParam()
    deviceId     = deviceConfig.get('id')

    log.setFileName('device-%s-%s' % (deviceConfig.get('name'), deviceId))
    if deviceConfig.get('loglevel'):
        log.setLevel(deviceConfig.get('loglevel'))

    #checkNotRunning(deviceId)
    process.setPid(deviceId, os.getpid())

    try:
        deviceObject = device.factory(deviceConfig)

        signal.signal(signal.SIGTERM, signalHandler) # $ kill <pid>
        signal.signal(signal.SIGINT, signalHandler)  # Ctrl-C

        deviceObject.start(block=True)
    except Exception, e:
        log.error('Device crashed: %s' % deviceId)
        log.error(utils.e2str(e))
