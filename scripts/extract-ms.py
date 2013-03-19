#!/home/green/bin/python
import os
import sys
from castepy.cell import Cell
from castepy.calc import CastepCalc
import castepy.bonds as bonds
from castepy.nmr import Magres
from castepy.format import load_magres, load_into_dict
from castepy.util import find_all_calcs, calc_from_path
from castepy.magres_constants import K_to_J
import numpy

cwd = ["."]
if len(sys.argv)>1:
    cwd = str(sys.argv[1])

calcs = map(calc_from_path, find_all_calcs(cwd))

find_s1 = str(sys.argv[2])
find_i1 = int(sys.argv[3])

for dir, name in calcs:
  calc = CastepCalc(dir, name)
  calc.load(exclude=['bonds', 'magres'])

  if not hasattr(calc, 'magres_file'):
    continue

  data = load_magres(calc.magres_file)

  if 'ms' not in data:
    print "# No magnetic shielding data for %s" % name
    continue

  for s1,i1,ms_tensor in data['ms']:
    if s1 == find_s1 and i1 == find_i1:
      print dir,name,"%s%d" % (s1,i1), numpy.trace(ms_tensor)/3.0

