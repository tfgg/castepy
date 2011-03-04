import os, sys
import numpy
from castepy import CastepCalc, Cell
import bonds
from ion import Ion, Ions, least_mirror
from nmr import Magres

def write_vector(v):
  return " ".join(map(str, v))

def write_matrix(m):
  return " ".join([" ".join(map(str,t)) for t in m])

def write_cell(cell):
  lines = [] 

  lines.append("lattice %s" % write_matrix(cell.lattice))

  for ion in cell.ions:
    p = ion.p
    if cell.ions_type == 'POSITIONS_FRAC':
      p = numpy.dot(cell.basis, p)
    lines.append("atom %s %d %s" % (ion.s, ion.i, write_vector(p)))

  for ion in cell.ions:
    if hasattr(ion, 'magres') and 'jc' in ion.magres:
      for (s, i), m in ion.magres['jc'].items():
        lines.append("jc %s %d %s %d %s" % (s, i, ion.s, ion.i, write_vector(m)))

  for ion in cell.ions:
    if hasattr(ion, 'magres') and 'ms' in ion.magres:
      lines.append("ms %s %d %s" % (ion.s, ion.i, write_vector(ion.magres['ms'])))
  
  for ion in cell.ions:
    if hasattr(ion, 'magres') and 'efg' in ion.magres:
      lines.append("efg %s %d %s" % (ion.s, ion.i, write_vector(ion.magres['efg'])))

  for bond in cell.ions.bonds:
    (s1, i1), (s2, i2), pop, r = bond
    p1 = cell.ions.get_species(s1, i1).p
    p2 = cell.ions.get_species(s2, i2).p

    d2, p2 = least_mirror(p2, p1,cell.basis, cell.lattice)

    if cell.ions_type == 'POSITIONS_FRAC':
      p1 = numpy.dot(cell.basis, p1)
      p2 = numpy.dot(cell.basis, p2)

    lines.append("bond %s %d %s %d %s %s" % (s1, i1, s2, i2, write_vector(p1), write_vector(p2)))  

  return "\n".join(lines)

def load_magres(magres_file):
  proc = {'lattice': lambda data: numpy.reshape(map(float, data), (3,3)),
          'atom': lambda data: (data[0], int(data[1]), map(float, data[2:])),
          'ms': lambda data: (data[0], int(data[1]), map(float, data[2:])),
          'efg': lambda data: (data[0], int(data[1]), map(float, data[2:])),
          'jc': lambda data: (data[0], int(data[1]), data[2], int(data[3]), map(float, data[4:])),}
  
  def clean(s):
    c = s.find('#')
    if c != -1:
      s = s[0:c]
    return s.strip()
 
  d = {}
  for line in magres_file.split('\n'):
    sline = clean(line).split()
    if len(sline) <= 1:
      continue

    tag = sline[0]
    data = sline[1:]

    if tag in proc:
      obj = proc[tag](data)
    else:
      obj = data

    if tag in d:
      d[tag].append(obj)
    else:
      d[tag] = [obj]

  return d

def load_into_ions(data):
  if len(data['lattice']) > 1:
    raise Exception("Too many lattice definitions.")

  ions = Ions()
  ions.lattice = data['lattice'][0]
  ions.basis = [[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]
  for s, i, p in data['atom']:
    ion = Ion(s, p)
    ions.add(ion)

    if not hasattr(ion, 'magres'):
      ion.magres = {}
  
  if 'jc' in data:
    for s1, i1, s2, i2, m in data['jc']:
      ion = ions.get_species(s2, i2)

      if 'jc' not in ion.magres:
        ion.magres['jc'] = {}
      ion.magres['jc'][(s1, i1)] = m
 
  if 'ms' in data:
    for s, i, m in data['ms']:
      ion = ions.get_species(s, i)

      if 'ms' not in ion.magres:
        ion.magres['ms'] = {}
      ion.magres['ms'] = m

  return ions

if __name__ == "__main__":
  if sys.argv[1] == 'load':
    magres_data = load_magres(open(sys.argv[2]).read())
    ions = load_into_ions(magres_data)

    for ion in ions: 
      if hasattr(ion, 'magres') and 'ms' in ion.magres:
        print ion.s, ion.i, ion.magres['ms']
      if hasattr(ion, 'magres') and 'jc' in ion.magres:
        jc_tensor = ion.magres['jc'].items()[0][1]
        print ion.s, ion.i, jc_tensor

  elif sys.argv[1] == 'dump':
    dir, file = os.path.split(sys.argv[2])
    name, _ = os.path.splitext(file)
    
    calc = CastepCalc(dir, name)

    print >>sys.stderr, "Loading cell file"
    c = Cell(calc.cell)

    if hasattr(calc, 'castep'):
      print >>sys.stderr, "Loading bonding information"
      bonds.add_bonds(c.ions, calc.castep)

    if hasattr(calc, 'magres'):
      print >>sys.stderr, "Loading magres information"
      m = Magres(calc.magres)
      m.annotate(c.ions)

    print write_cell(c)
