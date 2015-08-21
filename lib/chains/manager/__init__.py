import Queue, threading, subprocess, json, time
from chains import service
import chains.service.process as serviceProcess
from chains.common import config, log, utils, ChainsException, ParameterException
from chains.common.amqp import AmqpDaemon, runWithSignalHandler

class Manager(AmqpDaemon):
    """
    Manager

    Responsibilities:
        - Starting and stopping service processes
        #- Keeping a list of enabled and available services at this host
        - Keeping a list of running services at this host
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
    # Services
    # =========================

    def action_startService(self, serviceConfig):
        """ Start a new service thread on this host """
        return serviceProcess.start(serviceConfig)

    def action_stopService(self, serviceId):
        """ Stop a running service thread on this host """
        return serviceProcess.stop(serviceId)

    '''
    def action_enableService(self, serviceId):
        """ Enable service """
        service.config.enableService(serviceId)
        self.sendReconfiguredEvent()

    def action_disableService(self, serviceId):
        """ Disable service """
        service.config.disableService(serviceId)
        self.sendReconfiguredEvent()

    def action_getServicesAvailable(self):
        """ List service IDs in services-available on this host """
        return service.config.getAvailableServiceList()

    def action_getServicesEnabled(self):
        """ List service IDs in services-enabled on this host """
        return service.config.getEnabledServiceList()

    def action_getServices(self):
        available = self.action_getServicesAvailable()
        enabled   = self.action_getServicesEnabled()
        started   = self.action_getServicesStarted()
        result    = {}
        for id in available:
            result[id] = {'enabled': (id in enabled), 'online': (id in started)}
        return result
    '''

    #def action_getServicesStarted(self):
    def action_getRunninServices(self):
        """ List service IDs for running service threads """
        return serviceProcess.getRunningServices().keys()


def main(id):
    log.setFileName('manager-%s' % id)
    runWithSignalHandler(Manager(id))


if __name__ == '__main__':
    main('master')
