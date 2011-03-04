#!/home/green/bin/python
# -*- coding: utf-8 -*-
# Add required potentials to given cell file. Optionally links files into directory containing cell file
import os
import sys
try:
  from castepy.cell import Cell
except ImportError:
  from cell import Cell

def add_potentials(pot_dir, dir_path, cell_file):
  if cell_file.__class__ != Cell:
    c = Cell(open(cell_file).read())
  else:
    c = cell_file

  species_pot_string = "%s %s_POT.ASC.DAT"
  species_pot = []
  required_files = set()
  for s, n in c.ions.species():
      species_pot.append(species_pot_string % (s, s))
      if os.path.isfile(os.path.join(pot_dir, "%s_AEPS.DAT" % s)):
        required_files.add(os.path.join(pot_dir, "%s_AEPS.DAT" % s))
      required_files.add(os.path.join(pot_dir, "%s_POT.ASC.DAT" % s))

  c.blocks['SPECIES_POT'] = species_pot
  return (c, required_files)

def link_files(required_files, dir_path):
  for f in required_files:
    if not os.path.isfile(f):
      raise Exception("Required potential file \"%s\" doesn't exist." % f)
    else:
      f = os.path.abspath(f)            
      d, filename = os.path.split(f)
      target = os.path.join(dir_path, filename)

      if not os.path.isfile(target):
        os.symlink(f, target)

if __name__ == "__main__":
  if len(sys.argv) < 2:
    raise Exception("Specify the directory containing the pseudopotentials")

  # Folder containing the potentials
  pot_dir = str(sys.argv[1])

  if len(sys.argv) < 3:
    raise Exception("Specify the cell file")

  # Cell file to be examined for potentials needed
  cell_file = str(sys.argv[2])
  
  # Directory the cell file is in
  dir_path, _ = os.path.split(cell_file)

  # Link in the potential files or not? Optional.
  link = False
  if len(sys.argv) > 3:
    if sys.argv[3] == "link":
      link = True

  # Write the cell file to a particular directory? (and link?)
  out_file = None
  link_dir = dir_path
  if len(sys.argv) > 4:
    out_file = sys.argv[4]
    link_dir, _ = os.path.split(out_file)

  c, required_files = add_potentials(pot_dir, dir_path, cell_file)

  if link:
    link_files(required_files, link_dir)

  c.jcoupling_shift_origin()

  if out_file is None:
    print c
  else:
    f = open(out_file, "w+")
    f.write(str(c))


