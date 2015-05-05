#!/usr/bin/env python2

# from chains.something import Event, State, Action

#def rule(event, state):
def rule():
    # initialization, first event match description
    # Will use Event class and have a simpler look
    event, state = yield {'node':'chainsmaster', 'dev':'timer', 'srv':'newminute'}
    # event, state = yield Event(node='chainsmaster', dev='timer', service='newminute')
    print "RULE: got new event %s and state %s" % (event, state)
    print "RULE: running some action"
    # next event to match:
    event, state = yield {'node':'chainsmaster', 'dev':'tellstick', 'srv':'lamp3', 'data':'on'}
    # event, state = yield Event(node='chainsmaster', dev='tellstick', service='lamp3', data='on')
    print "RULE: got event %s and state %s" % (event, state)
    print "RULE: running some action again"

#myrule = rule('event','state')
#print dir(myrule)
