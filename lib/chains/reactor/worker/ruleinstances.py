            
# RuleInstances
# 
# List of instances for a single rule
# F.ex. if rule A has maxCount=2, then the RuleInstances for rule A
# has a list of 2 instances of RuleRunner for rule A.
# 
# Starts out with 0 instances and each time the first event in rule
# is matched, it spawns a new runner, until maxCount is reached.
# 
# All incoming events are passed to all active RuleRunner instances.
#
class RuleInstances:

    def __init__(self, rule, maxCount, context):

        self.maxCount = maxCount  # number of paralell instances allowed
        self.rule     = rule      # the rule definition (generator) itself
        self.runners  = []        # active rule runners
        self.context  = context

        # We need the first event in rule, so we copy it
        # to avoid wrecking the generator
        blueprint = copy.copy(rule) # no need, since () ?
        self.event = next(blueprint(None))


    def onEvent(self, event):

        # If event matches first event in rule, spawn new runner,
        # as long as maxCount not reached
        if event.match(self.event):

            if len(self.runners) < self.maxCount:
                self.debug("spawn new runner since count is %s < maxCount %s" % (len(self.runners), self.maxCount))
                rule = copy.copy(self.rule) # no need, since () ?
                runner = RuleRunner(rule, self.context)
                self.runners.append(runner)
            else:
                self.debug("do not spawn new runner since count is %s < maxCount %s" % (len(self.runners), self.maxCount))

        # Pass event to all active runners
        for runner in self.runners:
            runner.onEvent(event)

    def debug(self, msg, data=None):
        debug("RuleInstances: #%s: %s" % (self.context.id, msg), data)
    
