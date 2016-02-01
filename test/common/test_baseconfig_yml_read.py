import os, binascii
import unittest
from chains.common.config import BaseConfig

class TestBaseConfigYmlRead(unittest.TestCase):
  """
  Test the parts of config that is specific to reading .yml files.
  The rest is tested in TestBaseConfigData, so we don't need to do that here.
  We simply load the .yml and check that we have the correct internal data structure.
  """

  def setUp(self):
    testConfig = '''main:
  test: testContent
  isMaster: true
  interval: 60
  server: testServer

othersection:
  test: testContent2
  some:
    nested:
      key: Some nested content
'''

    fileName = binascii.b2a_hex(os.urandom(15))
    fullFileName = '/tmp/%s.yml' % fileName
    with open(fullFileName, 'w') as text_file:
      text_file.write(testConfig)

    self.testBaseConfig = BaseConfig(file=fullFileName)
    self.fullFileName = fullFileName

  def test_When_loading_a_yml_file_implicitly_It_creates_the_correct_data_structure(self):
    self.checkInternalDataOk()

  def test_When_loading_a_yml_file_explicitly_It_creates_the_correct_data_structure(self):
    self.testBaseConfig = BaseConfig()
    self.assertEquals({}, self.testBaseConfig._data)
    self.testBaseConfig.load(self.fullFileName)
    self.checkInternalDataOk()

  def checkInternalDataOk(self):
    expect = {
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

    self.assertEqual(expect, self.testBaseConfig.data())

if __name__ == '__main__':
  unittest.main()
