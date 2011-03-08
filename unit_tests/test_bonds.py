import unittest
import cell
import bonds

class TestBonds(unittest.TestCase):
  calc1_path = "test_data/ethanol/ethanol"

  def test_ethanol(self):
    """
      Read in ethanol cell and bonds and check they're correct.
    """

    c = cell.Cell(open("%s.cell" % self.calc1_path).read())
    castep_file = open("%s.castep" % self.calc1_path).read()
    bonds.add_bonds(c.ions, castep_file)

    self.assertEqual(len(c.ions.bonds), 8)

    for O_ion in c.ions.get_species('O'):
      self.assertEqual(len(O_ion.bonds), 2)
    
    for C_ion in c.ions.get_species('C'):
      self.assertEqual(len(C_ion.bonds), 4)
    
    for H_ion in c.ions.get_species('H'):
      self.assertEqual(len(H_ion.bonds), 1)


if __name__ == "__main__":
  unittest.main()

