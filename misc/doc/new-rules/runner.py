#!/usr/bin/env python2

# array holding active rules with next matches
rules = []

# importing rules from rules files
from rule1 import rule as rule1


# some test values we'll send to the rule
state = '{state of things}'
event1 = '{first event}'
event2 = '{second event}'

try:
    my_rule1 = rule1()
    #my_rule1 = rule1(0,0)
    nextmatch = next(my_rule1)
    print "RUNNER: next match: %s" % str(nextmatch)
    nextmatch = my_rule1.send([event1, state])
    print nextmatch
    nextmatch = my_rule1.send([event2, state])
    print nextmatch
except StopIteration:
    print "rule is done"
