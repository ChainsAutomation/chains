import Queue, threading, subprocess, json, time
from chains import device
import chains.device.process as deviceProcess
from chains.common import config, log, utils, ChainsException, ParameterException
from chains.common.amqp import AmqpDaemon, runWithSignalHandler

class Manager(AmqpDaemon):
    """
    Manager

    Responsibilities:
        - Starting and stopping device processes
        #- Keeping a list of enabled and available devices at this host
        - Keeping a list of running devices at this host
    """

    def __init__(self, id):
        log.info('Starting manager')
        AmqpDaemon.__init__(self, 'manager', id)

    def run(self):
        self.sendOnlineEvent()
        self.listen()
        self.sendOfflineEvent()

    def sendReconfiguredEvent(self):
        self.sendEvent('reconfigured', {'value': True})

    # =========================
    # Devices
    # =========================

    def action_startDevice(self, deviceConfig):
        """ Start a new device thread on this host """
        deviceProcess.start(deviceConfig)

    def action_stopDevice(self, deviceId):
        """ Stop a running device thread on this host """
        deviceProcess.stop(deviceId)

    '''
    def action_enableDevice(self, deviceId):
        """ Enable device """
        device.config.enableDevice(deviceId)
        self.sendReconfiguredEvent()

    def action_disableDevice(self, deviceId):
        """ Disable device """
        device.config.disableDevice(deviceId)
        self.sendReconfiguredEvent()

    def action_getDevicesAvailable(self):
        """ List device IDs in devices-available on this host """
        return device.config.getAvailableDeviceList()

    def action_getDevicesEnabled(self):
        """ List device IDs in devices-enabled on this host """
        return device.config.getEnabledDeviceList()

    def action_getDevices(self):
        available = self.action_getDevicesAvailable()
        enabled   = self.action_getDevicesEnabled()
        started   = self.action_getDevicesStarted()
        result    = {}
        for id in available:
            result[id] = {'enabled': (id in enabled), 'online': (id in started)}
        return result
    '''

    #def action_getDevicesStarted(self):
    def action_getRunninDevices(self):
        """ List device IDs for running device threads """
        return deviceProcess.getRunningDevices().keys()


def main(id):
    log.setFileName('manager-%s' % id)
    runWithSignalHandler(Manager(id))


if __name__ == '__main__':
    host = utils.getHostName().split('.')[0]
    main(host)
