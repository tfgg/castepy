#!/home/green/bin/python

"""
  Only show couplings where the coupling in the opposite direction exists in another calculation.
"""

import castepy.report

import os
import sys
from castepy.input.cell import Cell
from castepy.calc import CastepCalc
from castepy.utils import find_all_calcs, calc_from_path
from castepy.magres_constants import K_to_J, gamma_iso
import numpy
import math

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

if len(sys.argv) >= 5 and sys.argv[4] != "X":
  find_s2 = str(sys.argv[4])
else:
  find_s2 = None

all_Js = {}

tensors = ['isc', 'isc_fc', 'isc_spin', 'isc_orbital_p', 'isc_orbital_d']

for dir, name in calcs:
  calc = CastepCalc(dir, name)
  calc.load(exclude=['bonds'])

  if not hasattr(calc, 'magres_file'):
    continue

  for tensor in tensors:
    try:
      getattr(calc.magres, tensor)
    except:
      print "# J-coupling not found for %s %s" % (dir,name)
      continue

  for tensor in tensors:
    for s1,i1,s2,i2,K_tensor in getattr(calc.magres, tensor):
      if (find_s is None and find_i is None) or (s2 == find_s and i2 == find_i) or (s1 == find_s and i1 == find_i) and (find_s2 is None or s2 == find_s2):

        if (s1,i1,s2,i2) not in all_Js:
          all_Js[(s1,i1,s2,i2)] = {}

        all_Js[(s1,i1,s2,i2)][tensor] = numpy.reshape(K_tensor, (3,3))

matching_Js = []

for (s1,i1,s2,i2),K_tensors in all_Js.items():
  if not (s2 == s1 and i2 == i1) and (s2,i2,s1,i1) in all_Js:
    matching_Js.append((s1,i1,s2,i2,K_tensors))

matching_Js = sorted(matching_Js, key=lambda (s1,i1,s2,i2,K_tensors): sorted(((s1,i1),(s2,i2))))

print "# Site 1, Site 2,", ", ".join(tensors), ", r"

for s1,i1,s2,i2,K_tensors in matching_Js:
  ion1 = calc.cell.ions.get_species(s1, i1)
  ion2 = calc.cell.ions.get_species(s2, i2)

  d2, dr = calc.cell.least_mirror(ion1.p, ion2.p)

  J_isos = []
  K_isos = []
  for tensor in tensors:
    J_isos.append(numpy.trace(K_to_J(K_tensors[tensor], s1, s2))/3.0)
    K_isos.append(numpy.trace(K_tensors[tensor])/3.0)

  print "%d%s%d\t" % (gamma_iso[s1],s1,i1) + "%d%s%d\t" % (gamma_iso[s2],s2,i2) + "\t".join(map(str, K_isos)) + "\t" + str(math.sqrt(d2))

