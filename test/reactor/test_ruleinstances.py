import unittest
from chains.reactor.worker import Context, RuleInstances
from chains.reactor.definition import Event
from chains.reactor.state import State
from chains.common import log
import rule1, rule2, rule3
import time

class TestRuleInstances(unittest.TestCase):

    def setUp(self):
        log.setLevel('debug')
        self.context = Context(State())
        self.context.test = {}
        self.context.state.set('timer.hour.data.value', 15)

    def test_When_event_matching_first_occur_A_new_runner_is_spawned(self):
        inst = RuleInstances('rule2', rule2, 1, self.context)
        self.assertEqual(len(inst.runners), 0)
        inst.onEvent(Event(device='tellstick', key='switch-1'))
        self.assertEqual(len(inst.runners), 1)

    def test_When_event_not_matching_first_occur_A_new_runner_is_not_spawned(self):
        inst = RuleInstances('rule2', rule2, 1, self.context)
        self.assertEqual(len(inst.runners), 0)
        inst.onEvent(Event(device='tellstick', key='foo'))
        self.assertEqual(len(inst.runners), 0)

    def test_When_maxcount_is_two_Two_and_only_two_runners_are_spawned(self):
        inst = RuleInstances('rule2', rule2, 2, self.context)
        self.assertEqual(len(inst.runners), 0)
        inst.onEvent(Event(device='tellstick', key='switch-1'))
        self.assertEqual(len(inst.runners), 1)
        inst.onEvent(Event(device='tellstick', key='switch-1'))
        self.assertEqual(len(inst.runners), 2)
        inst.onEvent(Event(device='tellstick', key='switch-1'))
        self.assertEqual(len(inst.runners), 2)

    def test_When_all_events_are_matched_The_runner_is_removed(self):
        inst = RuleInstances('rule2', rule2, 1, self.context)
        self.assertEqual(len(inst.runners), 0)
        inst.onEvent(Event(device='tellstick', key='switch-1'))
        self.assertEqual(len(inst.runners), 1)
        inst.onEvent(Event(device='tellstick', key='switch-2'))
        time.sleep(0.1)
        self.assertEqual(len(inst.runners), 0)

    def test_When_event_occurs_They_are_passed_to_runner(self):
        inst = RuleInstances('rule2', rule2, 1, self.context)
        self.assertFalse( self.context.test.has_key('event-2.1-seen') )
        self.assertFalse( self.context.test.has_key('event-2.2-seen') )

        inst.onEvent(Event(device='tellstick', key='switch-1'))
        if len(inst.runners) > 0:
            inst.runners[0].wait()
        self.assertTrue( self.context.test.has_key('event-2.1-seen') )
        self.assertFalse( self.context.test.has_key('event-2.2-seen') )

        inst.onEvent(Event(device='tellstick', key='switch-2'))
        if len(inst.runners) > 0:
            inst.runners[0].wait()
        self.assertTrue( self.context.test.has_key('event-2.1-seen') )
        self.assertTrue( self.context.test.has_key('event-2.2-seen') )

