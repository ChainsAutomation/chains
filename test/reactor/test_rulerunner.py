import unittest
from chains.reactor.worker import Context, RuleRunner
from chains.reactor.definition import Event
from chains.reactor.state import State
from chains.common import log
import rule1, rule2
import time

class TestRuleRunner(unittest.TestCase):

    def setUp(self):
        log.setLevel('debug')
        self.context = Context(State())
        # We use this as a poor man's MockAction. Rules will set keys here
        # to indicate how far in the rule's steps we've got to.
        self.context.test = {}

    # Simple tests where rule has one event

    def test_When_event_rule_waits_for_occurs_Rule_iterates_to_next_step(self):
        runner = RuleRunner('rule1', self.context, rule1)
        self.assertFalse( self.context.test.has_key('event-seen') )
        runner.onEvent(Event(device='tellstick', key='switch-2'))
        runner.wait()
        self.assertTrue( self.context.test.has_key('event-seen') )

    def test_When_event_rule_does_not_wait_for_occurs_Rule_does_not_iterate_to_next_step(self):
        runner = RuleRunner('rule1', self.context, rule1)
        self.assertFalse( self.context.test.has_key('event-seen') )
        runner.onEvent(Event(device='tellstick', key='switch-3'))
        runner.wait()
        self.assertFalse( self.context.test.has_key('event-seen') )

    def test_When_rule_has_no_more_events_It_is_complete(self):
        runner = RuleRunner('rule1', self.context, rule1)
        self.assertFalse(runner.isComplete)
        runner.onEvent(Event(device='tellstick', key='switch-2'))
        runner.wait()
        self.assertTrue(runner.isComplete)

    def test_When_rule_has_more_events_It_is_not_complete(self):
        runner = RuleRunner('rule1', self.context, rule1)
        self.assertFalse(runner.isComplete)
        runner.onEvent(Event(device='tellstick', key='switch-3'))
        runner.wait()
        self.assertFalse(runner.isComplete)

    # More complex tests where rule has multiple events,
    # checks value in state, and runs callback on complete

    def test_When_rule_has_many_events_It_iterates_correctly(self):

        self.context.state.set('timer.hour.data.value', 17)
        runner = RuleRunner('rule2', self.context, rule2)

        # Before any events, rule does nothing
        self.assertFalse( self.context.test.has_key('event1-seen') )
        self.assertFalse( self.context.test.has_key('event2-seen') )
        self.assertFalse( self.context.test.has_key('event3-seen') )

        # When event that is not in rule occurs, nothing happens
        runner.onEvent(Event(device='tellstick', key='foo'))
        runner.wait()
        self.assertFalse( self.context.test.has_key('event1-seen') )
        self.assertFalse( self.context.test.has_key('event2-seen') )
        self.assertFalse( self.context.test.has_key('event3-seen') )

        # When event occurs that matches first event in rule, it iterates to next step
        runner.onEvent(Event(device='tellstick', key='switch-1'))
        runner.wait()
        self.assertTrue( self.context.test.has_key('event1-seen') )
        self.assertFalse( self.context.test.has_key('event2-seen') )
        self.assertFalse( self.context.test.has_key('event3-seen') )

        # When another event that is not in rule occurs, nothing happens
        runner.onEvent(Event(device='tellstick', key='foo'))
        runner.wait()
        self.assertTrue( self.context.test.has_key('event1-seen') )
        self.assertFalse( self.context.test.has_key('event2-seen') )
        self.assertFalse( self.context.test.has_key('event3-seen') )

        # When event occurs that matches second event in rule, it iterates another step
        runner.onEvent(Event(device='tellstick', key='switch-2'))
        runner.wait()
        self.assertTrue( self.context.test.has_key('event2-seen') )
        self.assertFalse( self.context.test.has_key('event3-seen') )

        # When event occurs that matches third event in rule, it iterates another step
        runner.onEvent(Event(device='tellstick', key='switch-3'))
        runner.wait()
        self.assertTrue( self.context.test.has_key('event3-seen') )

    def test_When_rule_conditional_does_not_match_It_stops(self):

        # Rule checks hour >= 16 before last event, so when
        # hour is 15, it should only do event1 + event2

        self.context.state.set('timer.hour.data.value', 15)
        runner = RuleRunner('rule2', self.context, rule2)

        runner.onEvent(Event(device='tellstick', key='switch-1'))
        runner.wait()

        runner.onEvent(Event(device='tellstick', key='switch-2'))
        runner.wait()

        runner.onEvent(Event(device='tellstick', key='switch-3'))
        runner.wait()

        self.assertTrue( self.context.test.has_key('event1-seen') )
        self.assertTrue( self.context.test.has_key('event2-seen') )
        self.assertFalse( self.context.test.has_key('event3-seen') )
    
    def test_When_rule_has_no_more_events_It_runs_complete(self):

        self.context.state.set('timer.hour.data.value', 17)
        runner = RuleRunner('rule2', self.context, rule2)

        self.assertFalse( self.context.test.has_key('complete') )

        runner.onEvent(Event(device='tellstick', key='switch-1'))
        runner.wait()

        runner.onEvent(Event(device='tellstick', key='switch-2'))
        runner.wait()

        self.assertFalse( self.context.test.has_key('complete') )

        runner.onEvent(Event(device='tellstick', key='switch-3'))
        runner.wait()

        self.assertTrue( self.context.test.has_key('complete') )

    def test_When_rule_stops_before_end_It_still_runs_complete(self):

        self.context.state.set('timer.hour.data.value', 15) # !!
        runner = RuleRunner('rule2', self.context, rule2)

        self.assertFalse( self.context.test.has_key('complete') )

        runner.onEvent(Event(device='tellstick', key='switch-1'))
        runner.wait()

        self.assertFalse( self.context.test.has_key('complete') )

        runner.onEvent(Event(device='tellstick', key='switch-2'))
        runner.wait()

        self.assertTrue( self.context.test.has_key('complete') )

if __name__ == '__main__':
    unittest.main()
