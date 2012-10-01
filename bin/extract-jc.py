#!/home/green/bin/python
import castepy.report

import os
import sys
from castepy.cell import Cell
from castepy.calc import CastepCalc
import castepy.bonds as bonds
from castepy.nmr import Magres
from castepy.format import load_magres, load_into_dict
from castepy.util import find_all_calcs, calc_from_path
from castepy.magres_constants import K_to_J, gamma_iso
import numpy

cwd = ["."]
if len(sys.argv)>1:
    cwd = str(sys.argv[1])

calcs = map(calc_from_path, find_all_calcs(cwd))

find_s2 = str(sys.argv[2])
find_i2 = int(sys.argv[3])

calcs = sorted(calcs, key=lambda (dir, name): (name, dir))

for dir, name in calcs:
  calc = CastepCalc(dir, name)
  calc.load(exclude=['bonds', 'magres'])

  if not hasattr(calc, 'magres_file'):
    continue

  data = load_magres(calc.magres_file)

  if 'isc' not in data:
    print "# J-coupling not found for %s %s" % (dir,name)
    continue

  for s1,i1,s2,i2,K_tensor in data['isc']:
    if (s2 == find_s2 and i2 == find_i2):
      print "%d%s%d" % (gamma_iso[s1],s1,i1), "%d%s%d" % (gamma_iso[s2],s2,i2), numpy.trace(K_to_J(K_tensor, s1, s2))/3.0, numpy.trace(K_tensor)/3.0, name, dir

#  if hasattr(calc, 'magres'):
#    calc.magres.annotate(calc.cell.ions)
#    
#    print "#", dir, name
#    print calc.params['cut_off_energy'], calc.cell.ions.get_species(s2, i2).magres['jc_prop'][(s1,i1)]['iso']

