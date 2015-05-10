import unittest
from chains.reactor.worker.context import Context
from chains.reactor.worker.ruleset import RuleSet
from chains.reactor.definition.event import Event
from chains.reactor.state import State
from chains.common import log
import rule1, rule2, rule3
import time

class TestRuleSet(unittest.TestCase):

    def setUp(self):
        log.setLevel('debug')
        self.context = Context(State())
        self.context.test = {}
        self.context.state.set('timer.hour.data.value', 18)

    """

        Complex scenario with multiple rules.

        1. First event triggers rule2+rule3
        2. Second event triggers rule1 + moved rule2 to next step,
           and would have done the same with rule3, but it is busy running actions.
        3. Last event is ignored by rule1 because it is done, moves rule2 to next step,
           and is ignored by rule3 because it is waiting for second event instead.

        @todo: more proper name and docmentation

        OCURRING                RULE1            RULE2           RULE3

        switch-1                -                E:switch-1      E:switch-1
        sleep 0.1                                event-2.1-seen  sleep 0.3
        switch-2                E:switch-2       E:switch-2      ignored:sleeping
        sleep 0.3               event-1.1-seen   event-2.2-seen  event-3.1-seen
        switch-3                ignored:done     E:switch-3      ignored:nomatch
        sleep 0.3               -                event-2.3-seen  -

    """
    def test_When_complex_concurrent_scenario_The_shit_works(self):
        ruleset = RuleSet(
            [
                (rule1, {'id': 'rule1', 'maxCount': 1}),
                (rule2, {'id': 'rule2', 'maxCount': 1}),
                (rule3, {'id': 'rule3', 'maxCount': 1})
            ],
            self.context
        )

        ruleset.onEvent(Event(device='tellstick', key='switch-1'))
        time.sleep(0.1)

        ruleset.onEvent(Event(device='tellstick', key='switch-2'))
        time.sleep(0.3)

        ruleset.onEvent(Event(device='tellstick', key='switch-3'))
        time.sleep(0.3)

        self.assertTrue( self.context.test.has_key('event-1.1-seen') )
        self.assertTrue( self.context.test.has_key('event-2.1-seen') )
        self.assertTrue( self.context.test.has_key('event-2.2-seen') )
        self.assertTrue( self.context.test.has_key('event-2.3-seen') )
        self.assertTrue( self.context.test.has_key('event-3.1-seen') )

    def test_When_complex_concurrent_scenario_The_shit_works_2(self):
        ruleset = RuleSet(
            [
                (rule1, {'id': 'rule1', 'maxCount': 1}),
                (rule3, {'id': 'rule3', 'maxCount': 2})
            ],
            self.context
        )

        # matches evt #1 in rule3 instance 1
        # ie. event-3.1-seen = 1
        ruleset.onEvent(Event(device='tellstick', key='switch-1'))
        time.sleep(0.1)

        # matches evt #1 in rule1 instance 1
        # and next evt (#2) in rule3 instance 1 - but it is busy so nothing happens
        # ie. event-1.1-seen = 1
        ruleset.onEvent(Event(device='tellstick', key='switch-2'))
        time.sleep(0.3)

        # matches evt #1 in rule3 instance 2
        # ie. event-3.1-seen = 2
        ruleset.onEvent(Event(device='tellstick', key='switch-1'))
        time.sleep(0.1)

        # matches evt #1 in rule1, which is done, so new is spawned
        # and matches next evt (#2) in rule3 instance 1 that is now done running actions
        # and matches next evt (#2) in rule3 instance 2 but it is busy
        # ie. event-1.1-seen = 2 and event-3.2-seen = 2
        ruleset.onEvent(Event(device='tellstick', key='switch-2'))
        time.sleep(0.3)

        self.assertEqual( self.context.test['event-1.1-seen'], 2 )
        self.assertEqual( self.context.test['event-3.1-seen'], 2 )
        self.assertEqual( self.context.test['event-3.2-seen'], 1 )
