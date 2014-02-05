import os.path, os
import unittest
import castepy.input.cell as cell

class TestCell(unittest.TestCase):
  cells_path = "test_data/castep_tests"

  def setUp(self):
    pass

  def test_al(self):
    """
      Read in ethanol cell and check contents.
    """

    for f in os.listdir(self.cells_path):
      print f

      path = os.path.join(self.cells_path, f)

      try:
        c = cell.Cell(open(path).read())
      except Exception, e:
        print type(e), e
    

if __name__ == "__main__":
  unittest.main()

