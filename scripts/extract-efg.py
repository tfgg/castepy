#!/usr/bin/env python

import os
import sys

from castepy.calc import CastepCalc
from castepy.util import find_all_calcs, calc_from_path
from castepy.magres_constants import efg_to_Cq

import numpy

cwd = ["."]
if len(sys.argv)>1:
    cwd = str(sys.argv[1])

calcs = map(calc_from_path, find_all_calcs(cwd))

if len(sys.argv) >= 3:
  find_s1 = str(sys.argv[2])
else:
  find_s1 = None

if len(sys.argv) >= 4:
  find_i1 = int(sys.argv[3])
else:
  find_i1 = None

for dir, name in calcs:
  calc = CastepCalc(dir, name)
  calc.load(exclude=['bonds'])

  try:
    getattr(calc.magres, 'efg')
  except:
    print "# EFG not found for %s %s" % (dir,name)
    continue

  for s1,i1,efg_tensor in calc.magres.efg:
    if (s1 == find_s1 or s1 is None) and (i1 == find_i1 or find_i1 is None):
      print dir,name,"%s%d" % (s1,i1), efg_to_Cq(efg_tensor, s1) 

