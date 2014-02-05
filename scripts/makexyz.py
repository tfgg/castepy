#!python
import sys
from castepy.cell import Cell

def get_val(s):
  return float(s.split('-')[3][:-5])

cells = []
for f in sorted(sys.argv[1:], key=get_val):
  print >>sys.stderr, f, get_val(f)
  cell = Cell(open(f).read())
  cells.append(cell)

for t, cell in enumerate(cells):
  print len(cell.ions)
  print float(t)

  for ion in cell.ions:
    print "%s %f %f %f" % (ion.s, ion.p[0], ion.p[1], ion.p[2])

