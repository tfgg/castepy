#!/usr/bin/env python

import castepy.report

import os
import sys
import numpy

from castepy.input.cell import Cell
from castepy.calc import CastepCalc, calcs_on_path

import castepy.output.bonds as bonds
from castepy.output.nmr import MagresResult

from castepy.magres_constants import K_to_J, gamma_iso

cwd = ["."]
if len(sys.argv)>1:
    cwd = str(sys.argv[1])

calcs = calcs_on_path(cwd, True)

find_s2 = str(sys.argv[2])
find_i2 = int(sys.argv[3])

#for calc in calcs:
#  print calc.params

if len(sys.argv) >= 5:
  tensor = sys.argv[4]
else:
  tensor = "isc"

calcs = sorted(calcs, key=lambda calc: float(calc.params.cut_off_energy[0]))

for calc in calcs:

  if not hasattr(calc, 'magres_file'):
    continue

  try:
    calc.magres.isc
  except:
    print "# J-coupling not found for %s %s" % (calc.dir, calc.name)
    continue

  for s1,i1,s2,i2,K_tensor in getattr(calc.magres, tensor):
    if (s2 == find_s2 and i2 == find_i2):
      K_tensor = numpy.reshape(K_tensor, (3,3))
      print calc.params.cut_off_energy[0], "%d%s%d" % (gamma_iso[s1],s1,i1), "%d%s%d" % (gamma_iso[s2],s2,i2), numpy.trace(K_to_J(K_tensor, s1, s2))/3.0, numpy.trace(K_tensor)/3.0, calc.name, calc.dir


