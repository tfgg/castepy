# -*- coding: utf-8 -*-
# Add required potentials to given cell file. Optionally links files into directory containing cell file

import os
import sys

from castepy.input.cell import Cell

def add_potentials(pot_dir, dir_path, cell_file, rel=False):
  if cell_file.__class__ != Cell:
    c = Cell(open(cell_file).read())
  else:
    c = cell_file

  species_pot_string = "%s %s_POT.ASC.DAT"
  species_pot = []
  required_files = set()
  for s, n in c.ions.species():
      species_pot.append(species_pot_string % (s, s))

      # Check for relativistic potential
      if rel and os.path.isfile(os.path.join(pot_dir, "%s_AEPS_REL.DAT" % s)):
        required_files.add((os.path.join(pot_dir, "%s_AEPS_REL.DAT" % s), "%s_AEPS.DAT" % s))
      elif os.path.isfile(os.path.join(pot_dir, "%s_AEPS.DAT" % s)):
        required_files.add((os.path.join(pot_dir, "%s_AEPS.DAT" % s), "%s_AEPS.DAT" % s))

      if rel and os.path.isfile(os.path.join(pot_dir, "%s_POT_REL.ASC.DAT" % s)):
        required_files.add((os.path.join(pot_dir, "%s_POT_REL.ASC.DAT" % s), "%s_POT.ASC.DAT" % s))
      else:
        required_files.add((os.path.join(pot_dir, "%s_POT.ASC.DAT" % s), "%s_POT.ASC.DAT" % s))

  c.blocks['SPECIES_POT'] = species_pot
  return (c, required_files)

def link_files(required_files, dir_path):
  for f, target_name in required_files:
    if not os.path.isfile(f):
      raise Exception("Required potential file \"%s\" doesn't exist." % f)
    else:
      f = os.path.abspath(f)            
      target = os.path.join(dir_path, target_name)

      if not os.path.isfile(target):
        os.symlink(f, target)

