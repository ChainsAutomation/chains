import os, binascii
import unittest
from chains.common.config import BaseConfig

class TestBaseConfigData(unittest.TestCase):
  """
  Test all the logic in BaseConfig that is not specific to the file-parsing,
  by populating from a data dict.
  """

  def setUp(self):
    testConfig = {
        'main': {
            'test': 'testContent',
            'isMaster': True,
            'interval': 60,
            'server': 'testServer'
        },
        'othersection': {
            'test': 'testContent2',
            'some': { 'nested': { 'key': 'Some nested content' }}
        }
    }
    self.testBaseConfig = BaseConfig(data=testConfig)

  def test_When_getting_key_It_returns_the_correct_value(self):
    self.assertEqual('testServer', self.testBaseConfig.get('server'))

  def test_When_checking_if_has_a_set_key_It_returns_true(self):
    self.assertEqual(True, self.testBaseConfig.has('server'))

  def test_When_checking_if_has_a_unset_key_It_returns_false(self):
    self.assertEqual(False, self.testBaseConfig.has('some-not-set-key'))

  def test_When_getting_a_value_as_boolean_It_returns_a_boolean(self):
    self.assertEqual(True, self.testBaseConfig.getBool('isMaster'))

  def test_When_getting_a_value_as_int_It_returns_an_int(self):
    self.assertEqual(60, self.testBaseConfig.getInt('interval'))

  def test_When_getting_data_for_main_It_returns_the_entire_section_dict(self):
    expect = {
        'interval': 60,
        'isMaster': True,
        'server': 'testServer',
        'test': 'testContent'
    }
    self.assertEqual(expect, self.testBaseConfig.data('main'))

  def test_When_getting_key_from_other_section_It_returns_the_correct_value(self):
    self.assertEqual('testContent2', self.testBaseConfig.get('test', 'othersection'))

  def test_When_getting_data_from_other_section_It_returns_the_entire_section_dict(self):
    expect = {
        'test': 'testContent2',
        'some': { 'nested': { 'key': 'Some nested content' }}
    }
    self.assertEqual(expect, self.testBaseConfig.data('othersection'))

  def test_When_getting_nested_key_with_full_path_It_returns_the_tip_value(self):
    self.assertEqual('Some nested content', self.testBaseConfig.get('some.nested.key', 'othersection'))

  def test_When_getting_nested_key_with_partial_pathIt_returns_the_dict_at_the_point(self):
    self.assertEqual(
        { 'key': 'Some nested content' },
        self.testBaseConfig.get('some.nested', 'othersection')
    )

  def test_When_getting_data_for_all_sections_It_returns_entire_config_dict(self):
    expect = {
        'main': {
            'interval': 60,
            'isMaster': True,
            'server': 'testServer',
            'test': 'testContent'
        },
        'othersection': {
            'test': 'testContent2',
            'some': { 'nested': { 'key': 'Some nested content' }}
        }
    }
    self.assertEqual(expect, self.testBaseConfig.data())

  def test_When_changing_a_simple_value_in_main_It_is_changed(self):
    self.testBaseConfig.set('test', 'testContentChanged')
    value = self.testBaseConfig.get('test')
    self.assertEquals('testContentChanged', value)

  def test_When_changing_a_simple_value_in_othersection_It_is_changed(self):
    self.testBaseConfig.set('test', 'testContentChanged2', 'othersection')
    value = self.testBaseConfig.get('test', 'othersection')
    self.assertEquals('testContentChanged2', value)

  def test_When_changing_a_nested_value_with_full_path_It_is_changed(self):
    self.testBaseConfig.set('some.nested.key', 'Some changed content', 'othersection')
    value = self.testBaseConfig.get('some.nested.key', 'othersection')
    self.assertEquals('Some changed content', value)

  def test_When_changing_a_nested_value_with_partial_path_It_is_changed(self):
    self.testBaseConfig.set('some.nested', {'foo':'bar','key':'moo'}, 'othersection')
    value = self.testBaseConfig.get('some.nested.key', 'moo')
    value = self.testBaseConfig.get('some.nested.foo', 'bar')

  def test_When_changing_a_nested_value_The_internal_data_is_properly_changed(self):
    self.testBaseConfig.set('some.nested.key', 'Some changed content', 'othersection')
    value = self.testBaseConfig.get('some', 'othersection')
    self.assertEquals({'nested':{'key':'Some changed content'}}, value)

if __name__ == '__main__':
  unittest.main()
