#!/home/green/bin/python
import castepy.report

import os
import sys
from castepy.cell import Cell
from castepy.calc import CastepCalc, calcs_on_path
import castepy.bonds as bonds
from castepy.nmr import MagresResult

from castepy.magres_constants import K_to_J, gamma_iso
import numpy

cwd = ["."]
if len(sys.argv)>1:
    cwd = str(sys.argv[1])

calcs = calcs_on_path(cwd, True)

find_s2 = str(sys.argv[2])
find_i2 = int(sys.argv[3])

if len(sys.argv) >= 6:
  find_s1 = str(sys.argv[4])
  find_i1 = int(sys.argv[5])
else:
  find_s1 = find_i1 = None

calcs = sorted(calcs, key=lambda calc: float(calc.params.cut_off_energy[0]))

tensors = ['isc', 'isc_fc', 'isc_spin', 'isc_orbital_p', 'isc_orbital_d']

print "# Cutoff, Atom1, Atom2, " + "".join("J%s, " % tensor for tensor in tensors) + "".join("K%s, " % tensor for tensor in tensors) + "calc_name, calc_dir"

for calc in calcs:
  if not hasattr(calc, 'magres_file'):
    continue

  try:
    calc.magres.isc
  except:
    print "# J-coupling not found for %s %s" % (calc.dir, calc.name)
    continue

  all_Js = {}
  for tensor in tensors:
    for s1,i1,s2,i2,K_tensor in getattr(calc.magres, tensor):
      if (s2 == find_s2 and i2 == find_i2):
        if find_s1 is not None and (s1 != find_s1 or i1 != find_i1):
          continue

        K_tensor = numpy.reshape(K_tensor, (3,3))

        if (s1,i1,s2,i2) not in all_Js:
          all_Js[(s1,i1,s2,i2)] = {}

        all_Js[(s1,i1,s2,i2)][tensor] = K_tensor

  for (s1, i1, s2, i2), K_tensors in all_Js.items():
    J_isos = []
    K_isos = []
    for tensor in tensors:
      J_isos.append(numpy.trace(K_to_J(K_tensors[tensor], s1, s2))/3.0)
      K_isos.append(numpy.trace(K_tensors[tensor])/3.0)

    print calc.params.cut_off_energy[0], "%d%s%d" % (gamma_iso[s1],s1,i1), "%d%s%d" % (gamma_iso[s2],s2,i2), "\t".join(map(str, J_isos)), "\t".join(map(str, K_isos)), calc.name, calc.dir

