#!python
import sys
from numpy import array
from castepy.cell import Cell

c1 = Cell(open(sys.argv[1]).read())
c2 = Cell(open(sys.argv[2]).read())
t = float(sys.argv[3])

for ion1 in c1.ions:
  ion2 = c2.ions.get_species(ion1.s, ion1.i)

  ion1.p = (1.0-t)*array(ion1.p) + t*array(ion2.p)

print c1

