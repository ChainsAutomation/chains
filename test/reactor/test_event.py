import unittest
from chains.reactor.definition.event import Event
from chains.common import log
#import rule1, rule2, rule3
#import time

class TestEvent(unittest.TestCase):

    def setUp(self):
        log.setLevel('debug')

    # Instantiation

    def test_When_passing_valid_kwargs_They_are_set(self):
        e = Event(service='dev', key='key', data='data')
        self.assertEqual(e.service, 'dev')
        self.assertEqual(e.key,    'key')
        self.assertEqual(e.data,   'data')

    def test_When_passing_valid_positional_args_They_are_set(self):
        e = Event('dev', 'key', 'data')
        self.assertEqual(e.service, 'dev')
        self.assertEqual(e.key,    'key')
        self.assertEqual(e.data,   'data')

    def test_When_passing_invalid_kwargs_TypeError_is_raised(self):
        try:
            e = Event(foo='invalid')
        except TypeError:
            return
        raise Exception('Expected TypeError, got none')

    def test_When_leaving_all_args_out_They_are_set_to_wildcard(self):
        e = Event()
        self.assertEqual(e.service, '*')
        self.assertEqual(e.key,    '*')
        self.assertEqual(e.data,   '*')

    def test_When_leaving_some_args_out_They_are_set_to_wildcard(self):
        e = Event(key='foo')
        self.assertEqual(e.service, '*')
        self.assertEqual(e.key,    'foo')
        self.assertEqual(e.data,   '*')

    # Matching

    def test_When_matching_exact_correct_values_They_are_matched(self):
        e1 = Event(service='dev', key='key', data='data')
        e2 = Event(service='dev', key='key', data='data')
        self.assertTrue(e1.match(e2))

    def test_When_matching_exact_incorrect_values_They_are_not_matched(self):
        e1 = Event(service='dev', key='key', data='data')
        e2 = Event(service='dev1', key='key1', data='data1')
        self.assertFalse(e1.match(e2))
        e2 = Event(service='dev1', key='key', data='data')
        self.assertFalse(e1.match(e2))
        e2 = Event(service='dev', key='key1', data='data')
        self.assertFalse(e1.match(e2))
        e2 = Event(service='dev', key='key', data='data1')
        self.assertFalse(e1.match(e2))

    def test_When_matching_wildcards_They_are_matched(self):
        e1 = Event(service='dev', key='*', data='*')
        e2 = Event(service='dev', key='key', data={'value': 12})
        self.assertTrue(e1.match(e2))

    def test_When_matching_wildcards_and_exact_incorrect_values_They_are_not_matched(self):
        e1 = Event(service='dev', key='*', data='*')
        e2 = Event(service='dev1', key='key', data={'value': 12})
        self.assertFalse(e1.match(e2))

    def test_When_matching_list_where_one_event_matches_It_matches(self):
        e1 = Event(service='dev', key='key', data='data')
        e2 = Event(service='dev', key='key', data='data2')
        e3 = Event(service='dev', key='key', data='data')
        self.assertTrue(e1.match([e2,e3]))

    def test_When_matching_list_where_both_events_match_It_matches(self):
        e1 = Event(service='dev', key='key', data='data')
        e2 = Event(service='dev', key='key', data='data')
        e3 = Event(service='dev', key='key', data='data')
        self.assertTrue(e1.match([e2,e3]))

    def test_When_matching_list_where_no_events_match_It_does_not_matches(self):
        e1 = Event(service='dev', key='key', data='data')
        e2 = Event(service='dev', key='key', data='data1')
        e3 = Event(service='dev', key='key', data='data2')
        self.assertFalse(e1.match([e2,e3]))
        
    # Matching on event data    

    def test_When_data_matches_exactly_It_is_a_match(self):
        e1 = Event(service='dev', key='key', data={'value': 2, 'type': 'humidity'}) # occurring
        e2 = Event(service='dev', key='key', data={'value': 2, 'type': 'humidity'}) # rule
        self.assertTrue(e1.match(e2))

    def test_When_data_does_not_match_It_is_not_a_match(self):
        e1 = Event(service='dev', key='key', data={'value': 2, 'type': 'humidity1'}) # occurring
        e2 = Event(service='dev', key='key', data={'value': 2, 'type': 'humidity2'}) # rule
        self.assertFalse(e1.match(e2))

    def test_When_data_matches_wildcard_It_is_a_match(self):
        e1 = Event(service='dev', key='key', data={'value': 2, 'type': 'humidity'}) # occurring
        e2 = Event(service='dev', key='key', data={'value': 2, 'type': '*'})        # rule
        self.assertTrue(e1.match(e2))

    def test_When_configured_data_is_subset_of_occuring_data_It_is_a_match(self):
        e1 = Event(service='dev', key='key', data={'value': 2, 'type': 'humidity'}) # occurring
        e2 = Event(service='dev', key='key', data={'value': 2})                     # rule
        self.assertTrue(e1.match(e2))

    def test_When_occurring_data_is_subset_of_configured_data_It_is_not_a_match(self):
        e1 = Event(service='dev', key='key', data={'value': 2})                      # occurring
        e2 = Event(service='dev', key='key', data={'value': 2, 'type': 'humidity'})  # rule
        self.assertFalse(e1.match(e2))

    def test_When_configured_data_is_subset_of_occuring_data_with_wildcard_It_is_a_match(self):
        e1 = Event(service='dev', key='key', data={'value': 2, 'type': 'humidity'}) # occurring
        e2 = Event(service='dev', key='key', data={'value': '*'})                   # rule
        self.assertTrue(e1.match(e2))

    def test_When_occurring_data_is_subset_of_configured_data_with_wildcard_It_is_not_a_match(self):
        e1 = Event(service='dev', key='key', data={'value': 2})                        # occurring
        e2 = Event(service='dev', key='key', data={'value': '*', 'type': 'humidity'})  # rule
        self.assertFalse(e1.match(e2))

    def test_When_deep_data_matches_exactly_It_is_a_match(self):
        e1 = Event(service='dev', key='key', data={'value': 2, 'extra': {'type': 'humidity'}}) # occurring
        e2 = Event(service='dev', key='key', data={'value': 2, 'extra': {'type': 'humidity'}}) # rule
        self.assertTrue(e1.match(e2))

    def test_When_deep_data_matches_wildcard_It_is_a_match(self):
        e1 = Event(service='dev', key='key', data={'value': 2, 'extra': {'type': 'humidity'}}) # occurring
        e2 = Event(service='dev', key='key', data={'value': 2, 'extra': {'type': '*'}})        # rule
        self.assertTrue(e1.match(e2))

    def test_When_deep_configured_data_is_subset_of_occuring_data_It_is_a_match_1(self):
        e1 = Event(service='dev', key='key', data={'value': 2, 'extra': {'type': 'humidity'}}) # occurring
        e2 = Event(service='dev', key='key', data={'value': 2})                                # rule
        self.assertTrue(e1.match(e2))

    # Hm.. Unsure about this one. Should we treat it as a match or not?
    def test_When_deep_configured_data_is_subset_of_occuring_data_It_is_a_match_2(self):
        e1 = Event(service='dev', key='key', data={'value': 2, 'extra': {'type': 'humidity'}}) # occurring
        e2 = Event(service='dev', key='key', data={'value': 2, 'extra': {}})                   # rule
        self.assertTrue(e1.match(e2))

    def test_When_deep_occurring_data_is_subset_of_configured_data_It_is_not_a_match_1(self):
        e1 = Event(service='dev', key='key', data={'value': 2})                                 # occurring
        e2 = Event(service='dev', key='key', data={'value': 2, 'extra': {'type': 'humidity'}})  # rule
        self.assertFalse(e1.match(e2))

    def test_When_deep_occurring_data_is_subset_of_configured_data_It_is_not_a_match_2(self):
        e1 = Event(service='dev', key='key', data={'value': 2, 'extra': {}})                    # occurring
        e2 = Event(service='dev', key='key', data={'value': 2, 'extra': {'type': 'humidity'}})  # rule
        self.assertFalse(e1.match(e2))

