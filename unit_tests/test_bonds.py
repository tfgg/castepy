import unittest
import castepy.input.cell as cell
import castepy.output.bonds as bonds

class TestBonds(unittest.TestCase):
  calc1_path = "test_data/ethanol/ethanol"

  def test_ethanol1(self):
    """
      Check basic bond parser is working for example of ethanol.
    """

    parsed_bonds = bonds.parse_bonds(open(self.calc1_path + ".castep").read())

    # Make sure we parse all the bonds
    self.assertEqual(len(parsed_bonds), 32)

  def test_ethanol2(self):
    """
      Read in ethanol cell and load bonds onto ions and check they're correct.
    """

    c = cell.Cell(open("%s.cell" % self.calc1_path).read())
    castep_file = open("%s.castep" % self.calc1_path).read()
    bonds.add_bonds(c.ions, castep_file)

    self.assertEqual(len(c.ions.bonds), 8)

    for O_ion in c.ions.species('O'):
      self.assertEqual(len(O_ion.bonds), 2)
    
    for C_ion in c.ions.species('C'):
      self.assertEqual(len(C_ion.bonds), 4)
    
    for H_ion in c.ions.species('H'):
      self.assertEqual(len(H_ion.bonds), 1)

if __name__ == "__main__":
  unittest.main()

