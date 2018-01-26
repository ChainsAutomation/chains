from __future__ import absolute_import
from chains.common import log, utils
from chains.common.amqp import AmqpDaemon, runWithSignalHandler, PREFIX_SERVICE, PREFIX_EVENT
from chains.reactor.state import State
from chains.reactor.worker.ruleset import RuleSet
from chains.reactor.worker.context import Context
from chains.reactor.definition.event import Event
from chains.reactor import config


class Reactor(AmqpDaemon):

    def __init__(self, id):

        log.info('Starting reactor')

        self.ruleset = None
        self.state = None

        AmqpDaemon.__init__(self, 'reactor', id)

        self.state = State()
        self.context = Context(self.state)
        rules = config.getData()
        self.ruleset = RuleSet(rules, self.context)

    def run(self):
        self.sendOnlineEvent()
        self.listen()
        self.sendOfflineEvent()

    def getConsumeKeys(self):
        keys = AmqpDaemon.getConsumeKeys(self)
        keys.append('%s%s.#' % (PREFIX_SERVICE, PREFIX_EVENT))
        return keys

    def onMessage(self, topic, data, correlationId):
        try:
            try:
                if self.state:

                    service = data.get('service')
                    device = data.get('device')
                    key = data.get('key')
                    values = data.get('data')

                    # Events without device are about the service itself
                    # For these, event.data is "raw" so we just set values as data for the key
                    if not device:
                        path = '%s._service.%s' % (service, key)
                        self.state.set(path, values)

                    # Other events are about a device inside the service
                    # For these, we merge in event.data under State.service.device.data,
                    # and merge any other non-sys keys from event under State.service.device.
                    else:
                        for prop in values:
                            path = '%s.%s.data.%s' % (service, device, prop)
                            self.state.set(path, values[prop])
                        for prop in data:
                            if prop not in ['service', 'device', 'key', 'data']:
                                path = '%s.%s.%s' % (service, device, prop)
                                self.state.set(path, data[prop])
            except Exception as e:
                log.error('Ignore error when setting state for event: %s = %s\n%s' % (topic, data, utils.e2str(e)))
            try:
                if self.ruleset:
                    if not data.get('ignore'):
                        self.ruleset.onEvent(Event(
                            service=data.get('service'),
                            device=data.get('device'),
                            key=data.get('key'),
                            data=data.get('data'),
                            time=data.get('time')
                        ))
            except Exception as e:
                log.error('Ignore error when running rules for event: %s = %s\n%s' % (topic, data, utils.e2str(e)))
        except Exception as e:
            log.error(utils.e2str(e))

    def action_getEnabledRules(self):
        return config.getEnabledNames()

    def action_getAvailableRules(self):
        return config.getAvailableNames()

    def action_enableRule(self, rule):
        try:
            config.enable(rule)
        except Exception as e:
            log.error('Ignore error when enabling rule: %s : %s' % (rule,utils.e2str(e)))
            return False
        self.action_reloadRules()

    def action_disableRule(self, rule):
        try:
            config.disable(rule)
        except Exception as e:
            log.error('Ignore error when disabling rule: %s : %s' % (rule,utils.e2str(e)))
            return False
        self.action_reloadRules()

    def action_reloadRules(self):
        try:
            reload(config)
            ruleset = RuleSet(config.getData(), self.context)
        except Exception as e:
            log.error('Ignore error when reloading rules: %s' % utils.e2str(e))
            return False
        del self.ruleset
        self.ruleset = ruleset
        return True

    def action_getState(self, key=None):
        return self.state.get(key)

    def action_setState(self, key, value):
        return self.state.set(key, value)

    def action_delState(self, key=None):
        return self.state.delete(key)


def main(id):
    log.setFileName('reactor-%s' % id)
    runWithSignalHandler(Reactor(id))

if __name__ == '__main__':
    log.setLevel('debug')
    main('chainsmaster')
