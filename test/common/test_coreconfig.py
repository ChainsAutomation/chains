import os, binascii
import unittest
from chains.common.config import CoreConfig

class TestCoreConfig(unittest.TestCase):

    def setUp(self):
        fileName = binascii.b2a_hex(os.urandom(15))
        self.path = '/tmp/%s.yml' % fileName

    def test_When_config_is_missing_It_is_auto_created(self):
        conf = CoreConfig(file=self.path)
        self.assertEquals('/etc/chains', conf.get('confdir'))
        self.assertEquals('{hostname}', conf.get('id', 'manager'))

    def test_When_getting_logfile_It_returns_the_correct_path(self):
        conf = CoreConfig(file=self.path)
        path = conf.getLogFile('manager')
        self.assertEquals('/var/log/chains/manager.log', path)

    def test_When_getting_pidfile_It_returns_the_correct_path(self):
        conf = CoreConfig(file=self.path)
        path = conf.getPidFile('manager')
        self.assertEquals('/var/run/chains/manager.pid', path)


if __name__ == '__main__':
  unittest.main()
