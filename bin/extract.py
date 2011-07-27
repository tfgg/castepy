#!/home/green/bin/python
import os
import sys
from castepy.cell import Cell
from castepy.calc import CastepCalc
import castepy.bonds as bonds
from castepy.nmr import Magres
from castepy.util import find_all_calcs, calc_from_path
import numpy

cwd = ["."]
if len(sys.argv)>1:
    cwd = str(sys.argv[1])

calcs = map(calc_from_path, find_all_calcs(cwd))

s1 = str(sys.argv[2])
i1 = int(sys.argv[3])

s2 = str(sys.argv[4])
i2 = int(sys.argv[5])

for dir, name in calcs:
  calc = CastepCalc(dir, name)
  calc.load(exclude=['bonds'])

  if hasattr(calc, 'magres'):
    calc.magres.annotate(calc.cell.ions)
    
    print "#", dir, name
    print calc.params['cut_off_energy'], calc.cell.ions.get_species(s2, i2).magres['jc_prop'][(s1,i1)]['iso']

