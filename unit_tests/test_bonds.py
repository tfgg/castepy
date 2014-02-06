import unittest
import castepy.input.cell as cell
from castepy.output.bonds import BondsResult, parse_bonds

class TestBonds(unittest.TestCase):
  calc1_path = "test_data/ethanol/ethanol"

  def test_ethanol1(self):
    """
      Check basic bond parser is working for example of ethanol.
    """

    parsed_bonds = parse_bonds(open(self.calc1_path + ".castep").read()).next()

    # Make sure we parse all the bonds
    self.assertEqual(len(parsed_bonds), 32)

  def test_ethanol2(self):
    """
      Read in ethanol cell and load bonds onto ions and check they're correct.
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
    
if __name__ == "__main__":
  unittest.main()

