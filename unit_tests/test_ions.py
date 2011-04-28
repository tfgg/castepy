from numpy import array

import unittest
import castepy.cell as cell
import castepy.ion as ion

class TestLeastMirror(unittest.TestCase):
  def setUp(self):
    pass

  def test_cart(self):
    lattice = array([(5.0, 0.0, 0.0),
                     (0.0, 5.0, 0.0),
                     (0.0, 0.0, 10.0),])

    basis = array([(1.0, 0.0, 0.0),
                   (0.0, 1.0, 0.0),
                   (0.0, 0.0, 1.0),])

    tests = [((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), 3.0, (1.0, 1.0, 1.0)),
             ((0.0, 0.0, 0.0), (4.0, 4.0, 9.0), 3.0, (-1.0, -1.0, -1.0)),
             ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0), 0.0, (0.0, 0.0, 0.0))]

    for p1, p2, min_exp, min_p_exp in tests:
      min, min_p = ion.least_mirror(p2, p1, basis, lattice)

      self.assertEqual(min, min_exp)
      self.assertItemsEqual(array(min_p), array(min_p_exp))

  def test_frac(self):
    lattice = array([(5.0, 0.0, 0.0),
                     (0.0, 5.0, 0.0),
                     (0.0, 0.0, 10.0),])

    basis = array([(5.0, 0.0, 0.0),
                   (0.0, 5.0, 0.0),
                   (0.0, 0.0, 10.0),])

    tests = [((0.0, 0.0, 0.0), (0.2, 0.2, 0.1), 3.0, (1.0, 1.0, 1.0)),
             ((0.0, 0.0, 0.0), (0.8, 0.8, 0.9), 3.0, (-1.0, -1.0, -1.0)),]

    for p1, p2, min_exp, min_p_exp in tests:
      min, min_p = ion.least_mirror(p2, p1, basis, lattice)

      self.assertEqual(min, min_exp)
      self.assertItemsEqual(array(min_p), array(min_p_exp))

if __name__ == "__main__":
 unittest.main()

