import unittest
import cell

class TestCell(unittest.TestCase):
  cell1_path = "test_data/ethanol/ethanol.cell"
  cell2_path = "test_data/lattice_not_implemented.cell"
  cell3_path = "test_data/lattice_wrong_shape.cell"

  def setUp(self):
    pass

  def test_ethanol(self):
    """
      Read in ethanol cell and check contents.
    """
    c = cell.Cell(open(self.cell1_path).read())

    self.assertEqual(c.ions_type, 'POSITIONS_ABS')
    self.assertEqual(c.ions_units, 'ang')
    self.assertEqual(c.lattice_type, 'LATTICE_CART')
    self.assertEqual(c.lattice_units, 'ang')

    self.assertEqual(len(c.ions), 9)
    self.assertEqual(len(c.ions.get_species('H')), 6)
    self.assertEqual(len(c.ions.get_species('C')), 2)
    self.assertEqual(len(c.ions.get_species('O')), 1)

  def test_lattice_unimplemented(self):
    with self.assertRaises(cell.Cell.LatticeNotImplemented):
      c = cell.Cell(open(self.cell2_path).read())

  def test_lattice_wrong_shape(self):
    with self.assertRaises(cell.Cell.LatticeWrongShape):
      c = cell.Cell(open(self.cell3_path).read())

if __name__ == "__main__":
  unittest.main()

