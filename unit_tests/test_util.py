import unittest
import castepy.util as util

class CalcFromPathTest(unittest.TestCase):
  tests_pass = [('foo/bar.cell', ('foo', 'bar')),
           ('bar.cell', ('', 'bar')),
           ('foo/bar', ('foo', 'bar')),]

  def test_success(self):
    for input, expected in self.tests_pass:
      self.assertEqual(util.calc_from_path(input), expected)

if __name__ == "__main__":
  unittest.main()

