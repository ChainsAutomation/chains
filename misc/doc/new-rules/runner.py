#!/usr/bin/env python2

from definition import Event, debug
import types

class Context:
    def __init__(self):
        # Possibly add some other useful stuff here, like amqp connection etc...
        self.state = {'timer.hour.data.value': 17} # todo.. this is just a test

class RuleRunner:

    def __init__(self, rule):
        debug('Init runner')
        self.isComplete = False
        self.context    = Context()           # Holds state and any other info useful to the rule 
        self.rule       = rule(self.context)  # The generator that is the configured rule
        self.events     = None                # The next/first event-list we're waiting to match
        self.getNext()                        # Go to the first event-list

    # Called by reactor each time any event occurs
    def onEvent(self, event):
        if self.isComplete:
            return
        debug('Occurring event:', event)
        if self.matchEvent(event):
            self.getNext()

    # Called once the rule is complete
    def onComplete(self):
        debug('Rule completed')
        self.isComplete = True

    # Go to next event in rule (after running any non-event steps before it)
    def getNext(self):
        try:
            # no need to send() new context all the time, since context is a pointer
            #data = self.rule.send(self.context)
            data = self.rule.next()
            if type(data) == types.ListType:
                self.events = data
            else:
                self.events = [data]
            debug('Wait for one of events:', self.events)
        except StopIteration:
            self.onComplete()

    # Check if the event that occurred matches one of the events in the
    # event-list we're waiting for. We use a list of expected events
    # to facilitate "OR".
    def matchEvent(self, occurringEvent):
        for expectedEvent in self.events:
            if occurringEvent.match(expectedEvent):
                debug('Matched event:', expectedEvent)
                return True
        return False

     
if __name__ == '__main__':
    import time
    from rule1 import rule as rule1
    runner = RuleRunner(rule1)
    time.sleep(0.5)
    runner.onEvent(Event(device='tellstick',key='switch-2')) # block!
    time.sleep(0.5)
    runner.onEvent(Event(device='tellstick',key='lamp-3'))
    time.sleep(0.5)
    runner.onEvent(Event(device='lirc',key='phillips',data={"value":"BTN_1"}))
    
