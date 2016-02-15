from __future__ import absolute_import
from __future__ import print_function
from chains.common import log
from chains.reactor.worker.ruleinstances import RuleInstances

# todo: implement timeout & onTimeout

# RuleSet
# Holds all RuleInstancess and passes events from AMQP to them


class RuleSet:

    def __init__(self, rules, context):
        self.sets = []
        for rule, config in rules:
            self.sets.append(RuleInstances(config['id'], rule, config['maxCount'], context))

    # Pass incoming events to all RuleInstancess
    def onEvent(self, event):
        log.notice("RuleSet: event occurred: %s" % event)
        for s in self.sets:
            s.onEvent(event)
