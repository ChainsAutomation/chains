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
	self.state   = None

        AmqpDaemon.__init__(self, 'reactor', id)

        self.state   = State()
        self.context = Context(self.state)
        self.ruleset = RuleSet(config.getData(), self.context)

    def run(self):
        self.sendOnlineEvent()
        self.listen()
        self.sendOfflineEvent()

    def getConsumeKeys(self):
        keys = AmqpDaemon.getConsumeKeys(self)
        keys.append('%s%s.#' % (PREFIX_SERVICE,PREFIX_EVENT))
        return keys

    def onMessage(self, topic, data, correlationId):
        try:
            topic = topic.split('.')
            try:
                if self.state:
                    self.state.set('.'.join(topic[1:]), data)
            except Exception, e:
                log.error(utils.e2str(e))
            try:
                if self.ruleset:
                    self.ruleset.onEvent(Event(
                        service = data['service'],
                        key    = data['key'],
                        data   = data['data']
                    ))
            except Exception, e:
                log.error(utils.e2str(e))
        except Exception, e:
            log.error(utils.e2str(e))

    def action_getEnabledRules(self):
        return config.getEnabledNames()
        
    def action_getAvailableRules(self):
        return config.getAvailableNames()

    def action_enableRule(self, rule):
        config.enable(rule)
        self.action_reloadRules()

    def action_disableRule(self, rule):
        config.disable(rule)
        self.action_reloadRules()

    def action_reloadRules(self):
        reload(config)
        del self.ruleset
        self.ruleset = RuleSet(config.getData(), self.context)

    def action_getState(self, key=None):
        return self.state.get(key)

    def action_setState(self, key, value):
        return self.state.set(key, value)

    def action_delState(self, key=None):
        return self.state.delete(key)

    """ needs l0ve, or deprecate...

    def action_getActiveRule(self, id):
        return self.worker.get(id)

    def action_listActiveRules(self, rule=None):
        return self.worker.list(rule)

    """

def main(id):
    log.setFileName('reactor-%s' % id)
    runWithSignalHandler(Reactor(id))

if __name__ == '__main__':
    log.setLevel('debug')
    main('master')
