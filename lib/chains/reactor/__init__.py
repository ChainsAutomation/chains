from chains.common import log, utils
from chains.common.amqp import AmqpDaemon, runWithSignalHandler
from chains.reactor import state, worker, dynamicArgs
import chains.reactor.rules.config

class Reactor(AmqpDaemon):

    def __init__(self, id):
        log.info('Starting reactor')
        AmqpDaemon.__init__(self, 'reactor', id)
        self.state = state.State()
        self.worker = worker.Worker(self)

    def run(self):
        self.sendOnlineEvent()
        self.listen()
        self.sendOfflineEvent()

    def getConsumeKeys(self):
        # todo: here we should get just the keys we need?
        keys = AmqpDaemon.getConsumeKeys(self)
        keys.append('de.#')
        return keys

    def onMessage(self, topic, data, correlationId):
        try:
            topic = topic.split('.')
            try:
                if self.worker:
                    self.worker.onEvent(data)
            except Exception, e:
                log.error(utils.e2str(e))
            try:
                if self.state:
                    self.state.set('.'.join(topic[1:]), data)
            except Exception, e:
                log.error(utils.e2str(e))
        except Exception, e:
            log.error(utils.e2str(e))

    def resolveArgs(self, args, state):
        return dynamicArgs.resolveArgs(args, state, self.state)

    def action_getEnabledRules(self):
        return chains.reactor.rules.config.getEnabledNames()
        
    def action_getAvailableRules(self):
        return chains.reactor.rules.config.getAvailableNames()

    def action_enableRule(self, rule):
        chains.reactor.rules.config.enable(rule)
        self.action_reloadRules()

    def action_disableRule(self, rule):
        chains.reactor.rules.config.disable(rule)
        self.action_reloadRules()

    def action_reloadRules(self):
        reload(chains.reactor.rules.config)
        self.worker = worker.Worker(self)

    def action_getActiveRule(self, id):
        return self.worker.get(id)

    def action_listActiveRules(self, rule=None):
        return self.worker.list(rule)

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
    main(utils.getHostName())
