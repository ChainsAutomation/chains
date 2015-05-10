
# RuleSet
# Holds all RuleInstacess and passes events from AMQP to them
class RuleSet:

    def __init__(self, rules):
        self.sets = []
        maxCount = 0 
        for rule in rules:
            maxCount += 1 # test
            context = Context(id=maxCount)
            self.sets.append(RuleInstaces(rule, maxCount, context))

    # Pass incoming events to all RuleInstacess
    def onEvent(self, event):
        debug("===============================================")
        debug("RuleSet: event occurred: %s" % event)
        debug("===============================================")
        for s in self.sets:
            s.onEvent(event)
            
