import os, sys

from castepy import Cell, Parameters
from nmr import Magres
import bonds

class CastepCalc:
  types = {'cell':'%s.cell',
           'param': '%s.param',
           'castep': '%s.castep',
           'magres': '%s.magres',}

  def __init__(self, dir=None, name=None):
    if dir is None:
      root = "."
    else:
      root = dir

    self.files = {}
  
    for t, file in self.types.items():
      file_path = os.path.join(root, file % name)
      if os.path.isfile(file_path):
        try:
          f = open(file_path)
          setattr(self, "%s_file" % t, f.read())
        except:
          pass

  def load(self):
    if hasattr(self, 'cell_file'):
      self.cell = Cell(self.cell_file)

    if hasattr(self, 'param_file'):
      self.param = Parameters(self.param_file)

    if hasattr(self, 'magres_file'):
      self.magres = Magres(self.castep_file)

    if hasattr(self, 'castep_file'):
      bonds.add_bonds(self.cell.ions, self.castep_file)

