import os, binascii
import unittest
from chains.common.config import CoreConfig

class TestCoreConfig(unittest.TestCase):

  def setUp(self):
    testConfig = '''[emptyconf]
foo = bar
'''

    fileName = binascii.b2a_hex(os.urandom(15))
    fullFileName = '/tmp/%s' % fileName
    with open(fullFileName, 'w') as text_file:
      text_file.write(testConfig)

    self.testCoreConfig = CoreConfig()
    self.testCoreConfig._file = fullFileName

  def test_When_config_has_no_main_section_It_creates_a_default_config(self):
    self.assertEqual('/etc/chains', self.testCoreConfig.get('confdir'))

if __name__ == '__main__':
  unittest.main()
