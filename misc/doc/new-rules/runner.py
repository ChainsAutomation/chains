#!/usr/bin/env python2

from definition import Event, debug
import types
import threading
import copy

class Context:
    def __init__(self, id):
        # Possibly add some other useful stuff here, like amqp connection etc...
        self.state = {'timer.hour.data.value': 17} # todo.. this is just a test
        self.id = id

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
            
# RuleInstaces
# 
# List of instances for a single rule
# F.ex. if rule A has maxCount=2, then the RuleInstaces for rule A
# has a list of 2 instances of RuleRunner for rule A.
# 
# Starts out with 0 instances and each time the first event in rule
# is matched, it spawns a new runner, until maxCount is reached.
# 
# All incoming events are passed to all active RuleRunner instances.
#
class RuleInstaces:

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
        debug("RuleInstaces: #%s: %s" % (self.context.id, msg), data)
    
            
# RuleRunner
# 
# Helper that handles running the rule generator
# 
# Checks if incoming event matches next event in rule,
# and if so iterates to next in the generator, causing
# it to run its next action(s) and yield the next event.
#
# The iterate-to-next step is run in a thread to ensure
# long running actions do not block handling of events
# that occur in the meantime.
#
class RuleRunner:

    def __init__(self, rule, context):
        self.isComplete = False
        self.context    = context
        self.rule       = rule(self.context)  # The generator that is the configured rule
        self.events     = None                # The next/first event-list we're waiting to match
        self.debug('Init runner')
        self.getNext()                        # Go to the first event-list

    # Handle occurring events
    def onEvent(self, event):

        # If we're not waiting for an event, we're running actions or we're done
        if not self.events:
            self.debug('Event ignored since not waiting for event: %s' % event)
            return

        # If event matches what we're waiting for, iterate to next step in rule
        self.debug('Event acted upon:', event)
        if event.match(self.events):
            self.events = None # While running actions, we're not waiting for events
            thread = threading.Thread(target=self.getNext) # Don't block when running actions
            thread.daemon = True
            thread.start()

    # Called once the rule is complete
    def onComplete(self):
        self.debug('Rule completed')
        self.events = None
        self.isComplete = True

    # Go to next event in rule
    def getNext(self):
        try:
            # Iterate to next step in rule, running any actions in between
            data = self.rule.next()
            if type(data) == types.ListType:
                self.events = data
            else:
                self.events = [data]
            # Rule is done running actions, and we're waiting for an event again
            self.debug('Wait for one of events:', self.events)
        # No more events? Then we're done.
        except StopIteration:
            self.onComplete()

    def debug(self, msg, data=None):
        debug("RuleRunner: #%s: %s" % (self.context.id, msg), data)

     
if __name__ == '__main__':
    import time
    from rule1 import rule as rule1
    from rule2 import rule as rule2
    ruleset = RuleSet([rule1,rule2])
    time.sleep(1)
    ruleset.onEvent(Event(device='tellstick',key='switch-2')) # block!
    time.sleep(1)
    ruleset.onEvent(Event(device='tellstick',key='lamp-3'))
    time.sleep(1)
    ruleset.onEvent(Event(device='lirc',key='phillips',data={"value":"BTN_1"}))
    time.sleep(1)
    ruleset.onEvent(Event(device='tellstick',key='switch-2')) # block!
    time.sleep(1)
    ruleset.onEvent(Event(device='tellstick',key='lamp-3'))
    time.sleep(1)
    ruleset.onEvent(Event(device='lirc',key='phillips',data={"value":"BTN_1"}))
    
