import os, binascii
import unittest
from chains.common.config import BaseConfig

class TestBaseConfig(unittest.TestCase):
  def setUp(self):
    testConfig = '''[main]
test = testContent
isMaster = True
interval = 60
server = testServer'''

    fileName = binascii.b2a_hex(os.urandom(15))
    fullFileName = '/tmp/%s' % fileName
    with open(fullFileName, 'w') as text_file:
      text_file.write(testConfig)

    self.testBaseConfig = BaseConfig([fullFileName])
    self.testBaseConfig.reload()

  def test_baseconfig_init(self):
    testBaseConfig = BaseConfig(['/tmp/tmp'])
    self.assertIsInstance(BaseConfig(['/tmp/tmp']), type(testBaseConfig))
    self.assertEqual({}, testBaseConfig.data())

  def test_baseconfig_loaded(self):
    self.assertEqual(True, self.testBaseConfig._loaded)

  def test_baseconfig_get(self):
    self.assertEqual('testServer', self.testBaseConfig.get('server'))

  def test_baseconfig_has(self):
    self.assertEqual(True, self.testBaseConfig.has('server'))

  def test_baseconfig_getBool(self):
    self.assertEqual(True, self.testBaseConfig.getBool('ismaster'))

  def test_baseconfig_getInt(self):
    self.assertEqual(60, self.testBaseConfig.getInt('interval'))

  def test_baseconfig_data(self):
    self.assertEqual({'main': {'interval': '60', 'ismaster': 'True', 'server': 'testServer', 'test': 'testContent'}}, self.testBaseConfig.data())

if __name__ == '__main__':
  unittest.main()
