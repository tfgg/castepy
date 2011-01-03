#!/home/green/bin/python
# -*- coding: utf-8 -*-
# Add required potentials to given cell file. Optionally links files into directory containing cell file
import os
import sys
try:
  from castepy.castepy import Cell
except ImportError:
  from castepy import Cell

def add_potentials(pot_dir, dir_path, cell_file, link):
  c = Cell(open(cell_file).read())

  species = c.get_species()

  species_pot_string = "%s %s_POT.ASC.DAT"
  species_pot = []
  required_files = set()
  for s in species:
      species_pot.append(species_pot_string % (s, s))
      if os.path.isfile(os.path.join(pot_dir, "%s_AEPS.DAT" % s)):
        required_files.add(os.path.join(pot_dir, "%s_AEPS.DAT" % s))
      required_files.add(os.path.join(pot_dir, "%s_POT.ASC.DAT" % s))

  if link:
    for f in required_files:
      if not os.path.isfile(f):
        raise Exception("Required potential file \"%s\" doesn't exist." % f)
      else:
        f = os.path.abspath(f)            
        d, filename = os.path.split(f)
        target = os.path.join(dir_path, filename)

        if not os.path.isfile(target):
          os.symlink(f, target)

  c.blocks['SPECIES_POT'] = species_pot
  return c

if __name__ == "__main__":
  if len(sys.argv) < 2:
    raise Exception("Specify the directory containing the potentials")

  pot_dir = str(sys.argv[1])

  if len(sys.argv) < 3:
    raise Exception("Specify the cell file")

  cell_file = str(sys.argv[2])
  dir_path, _ = os.path.split(cell_file)

  link = False
  if len(sys.argv) >=4:
    if sys.argv[3] == "link":
      link = True

  c = add_potentials(pot_dir, dir_path, cell_file, link)
  c.hack_perturb_origin()
  print c

