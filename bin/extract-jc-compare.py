#!/home/green/bin/python

"""
  Only show couplings where the coupling in the opposite direction exists in another calculation.
"""

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
calcs = sorted(calcs, key=lambda (dir, name): name)

if len(sys.argv) >= 4:
  find_s = str(sys.argv[2])
  find_i = int(sys.argv[3])
else:
  find_s = find_i = None

all_Js = {}

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
    if (find_s is None and find_i is None) or (s2 == find_s and i2 == find_i) or (s1 == find_s and i1 == find_i):
      all_Js[(s1,i1,s2,i2)] = K_tensor

matching_Js = []

for (s1,i1,s2,i2),K_tensor in all_Js.items():
  if not (s2 == s1 and i2 == i1) and (s2,i2,s1,i1) in all_Js:
    matching_Js.append((s1,i1,s2,i2,K_tensor))

matching_Js = sorted(matching_Js, key=lambda (s1,i1,s2,i2,K_tensor): sorted(((s1,i1),(s2,i2))))

for s1,i1,s2,i2,K_tensor in matching_Js:
  print "%d%s%d" % (gamma_iso[s1],s1,i1), "%d%s%d" % (gamma_iso[s2],s2,i2), numpy.trace(K_to_J(K_tensor, s1, s2))/3.0, numpy.trace(K_tensor)/3.0

#  if hasattr(calc, 'magres'):
#    calc.magres.annotate(calc.cell.ions)
#    
#    print "#", dir, name
#    print calc.params['cut_off_energy'], calc.cell.ions.get_species(s2, i2).magres['jc_prop'][(s1,i1)]['iso']

