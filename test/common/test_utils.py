import unittest, os
from chains.common.utils import *

class TestUtils(unittest.TestCase):
  def test_lcfirst(self):
    testString = 'Something'
    lowerCasedString = 'something'
    self.assertEqual(lowerCasedString, lcfirst(testString))

  def test_ucfirst(self):
    testString = 'something'
    upperCasedString = 'Something'
    self.assertEqual(upperCasedString, ucfirst(testString))

  def test_e2str(self):
    testException = Exception('testException')
    self.assertEqual('<type \'exceptions.Exception\'>: testException\nNone\n', e2str(testException))

  def test_stripTags(self):
    testString = '<h1>Header</h1> <p>Test paragraph</p>'
    self.assertEqual('Header Test paragraph', stripTags(testString))

  def test_formatDuration(self):
    minute = 60
    hour = minute * 60
    day = hour * 24
    week = day * 7
    self.assertEqual('1.00 m', formatDuration(minute))
    self.assertEqual('1.00 h', formatDuration(hour))
    self.assertEqual('1.00 d', formatDuration(day))
    self.assertEqual('1.00 w', formatDuration(week))

  def test_formatTime(self):
    os.environ['TZ'] = 'Europe/London'
    testTime = 1111885200
    self.assertEqual('2005-03-27 02:00:00', formatTime(testTime))

  def test_caseSplit(self):
    testText = 'CamelCaseStringToTestWith'
    self.assertEqual(['camel', 'case', 'string', 'to', 'test', 'with'], caseSplit(testText))

  def test_formatDecimals(self):
    decimalNumber = '12.34'
    decimalNumberWithMoreDecimals = '12.345678'
    integerNumber = '12'
    self.assertEqual(decimalNumber, formatDecimals(decimalNumberWithMoreDecimals))
    self.assertEqual('12.00', formatDecimals(integerNumber))
    self.assertEqual(decimalNumberWithMoreDecimals, formatDecimals(decimalNumberWithMoreDecimals, 6))

  def test_split(self):
    s = 'hello world'
    self.assertEqual(s.split(), ['hello', 'world'])
    # check that s.split fails when the separator is not a string
    with self.assertRaises(TypeError):
      s.split(2)

if __name__ == '__main__':
  unittest.main()
