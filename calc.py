import os, sys

from castepy import Parameters
from cell import Cell
from nmr import Magres

import energy
import bonds

class CastepCalc:
  types = {'cell':'%s.cell',
           'param': '%s.param',
           'castep': '%s.castep',
           'magres': '%s.magres',}

  def __init__(self, dir=None, name=None, include=None, exclude=None):
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

    if include is not None:
      self.load(include, exclude)

  def load(self, include=None, exclude=None):
    if include is None:
      include = set(["cell", "params", "magres", "bonds", "energy"])
    else:
      include = set(include)

    if exclude is None:
      exclude = set()
    else:
      exclude = set(exclude)

    to_load = include - exclude

    if hasattr(self, 'cell_file') and "cell" in to_load:
      self.cell = Cell(self.cell_file)

    if hasattr(self, 'param_file') and "params" in to_load:
      self.params = Parameters(self.param_file)

    if hasattr(self, 'magres_file') and "magres" in to_load:
      self.magres = Magres(self.magres_file)
      self.magres.annotate(self.cell.ions)

    if hasattr(self, 'castep_file') and "bonds" in to_load:
      try:
        bonds.add_bonds(self.cell.ions, self.castep_file)
      except Exception:
        pass

    if hasattr(self, 'castep_file') and "energy" in to_load:
      try:
        self.energy = energy.parse(self.castep_file)
      except energy.CantFindEnergy:
        self.energy = None
