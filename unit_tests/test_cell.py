import unittest
import numpy
import castepy.input.cell as cell

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
    
    lattice = [[6.0,0.0,0.0],[0.0,6.0,0.0],[0.0,0.0,6.0]]

    self.assertTrue(numpy.allclose(c.lattice, lattice, rtol=1e-05, atol=1e-08))

    self.assertEqual(len(c.ions), 9)
    self.assertEqual(len(c.ions.species('H')), 6)
    self.assertEqual(len(c.ions.species('C')), 2)
    self.assertEqual(len(c.ions.species('O')), 1)

    C1 = c.ions.C1
    
    self.assertEqual(len(c.ions.within(C1, 1.5)), 4)

  def test_lattice_abc(self):
    c = cell.Cell(open(self.cell2_path).read())

    lattice = [[6.0,0.0,0.0],[0.0,6.0,0.0],[0.0,0.0,6.0]]

    self.assertTrue(numpy.allclose(c.lattice, lattice, rtol=1e-05, atol=1e-08))

  def test_lattice_wrong_shape(self):
    with self.assertRaises(cell.Cell.LatticeWrongShape):
      c = cell.Cell(open(self.cell3_path).read())

  def test_to_string(self):
    """
      Does generating a .cell file from the object work and is it consistent?
    """
    c1 = cell.Cell(open(self.cell1_path).read())
    c2 = cell.Cell(str(c1))

    self.assertEqual(str(c1), str(c2))

if __name__ == "__main__":
  unittest.main()

