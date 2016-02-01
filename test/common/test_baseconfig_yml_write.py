import os, binascii
import unittest
from chains.common.config import BaseConfig

class TestBaseConfigYmlWrite(unittest.TestCase):
  """
  Test the parts of config that is specific to writing .yml files.
  """

  def setUp(self):
    fileName = binascii.b2a_hex(os.urandom(15))
    self.path = '/tmp/%s.yml' % fileName

  def test_When_loading_a_yml_file_It_creates_the_correct_data_structure(self):

    conf = BaseConfig(file=self.path)
    self.assertEquals(False, conf.has('foo'))
    conf.set('foo', 'bar')
    self.assertEquals('bar', conf.get('foo'))
    conf.save()

    conf = BaseConfig(file=self.path)
    self.assertEquals('bar', conf.get('foo'))

if __name__ == '__main__':
  unittest.main()
