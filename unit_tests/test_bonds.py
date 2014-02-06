import unittest
import castepy.input.cell as cell
from castepy.output.bonds import BondsResult, parse_bonds

class TestBonds(unittest.TestCase):
  calc1_path = "test_data/ethanol/ethanol"

  def test_ethanol_basic(self):
    """
      Check basic bond parser is working for example of ethanol.
    """

    parsed_bonds = parse_bonds(open(self.calc1_path + ".castep").read()).next()

    # Make sure we parse all the bonds
    self.assertEqual(len(parsed_bonds), 32)

  def test_ethanol_bond_result(self):
    """
      Check BondsResult is doing its job.
    """

    #c = cell.Cell(open("%s.cell" % self.calc1_path).read())
    castep_file = open("%s.castep" % self.calc1_path).read()

    bonds = BondsResult.load(castep_file).next()

    self.assertEqual(len(bonds.bonds), 8)
    self.assertEqual(len(bonds.index[('C',1)]), 4)
    self.assertEqual(len(bonds.index[('C',2)]), 4)
    self.assertEqual(len(bonds.index[('O',1)]), 2)
    self.assertEqual(len(bonds.index[('H',1)]), 1)
    self.assertEqual(len(bonds.index[('H',2)]), 1)
    self.assertEqual(len(bonds.index[('H',3)]), 1)
    self.assertEqual(len(bonds.index[('H',4)]), 1)
    self.assertEqual(len(bonds.index[('H',5)]), 1)
    self.assertEqual(len(bonds.index[('H',6)]), 1)
   
  def test_ethanol_common(self):
    """
      Check function to calculate common neighbours
    """

    castep_file = open("%s.castep" % self.calc1_path).read()

    bonds = BondsResult.load(castep_file).next()

    self.assertTrue(('C',2) in bonds.common(('C',1),('O',1)))
    self.assertTrue(('O',1) in bonds.common(('H',6),('C',2)))

if __name__ == "__main__":
  unittest.main()

