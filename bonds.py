import re
import sys
import castepy
import ion
from ion import least_mirror
import numpy
from numpy import dot, array
import math

def parse_bonds(castep_file):
  """
    Parse bonding information from .castep file
  """
  
  regex_block = re.compile("     Bond                     Population      Length \(A\).*?\n[=]+\n(.*?)\n[=]+", re.M | re.S)
  regex_line = re.compile("\s+([A-Za-z]+)\s+([0-9]+)\s+--\s+([A-Za-z]+)\s+([0-9]+)\s+([0-9\-\.]+)\s+([0-9\-\.]+)\n")

  bond_blocks = regex_block.findall(castep_file)

  if len(bond_blocks) == 0:
    return []
  
  block = bond_blocks[len(bond_blocks)-1]

  bonds = []
  for s1, i1, s2, i2, population, r in regex_line.findall(block):
    bonds.append(((s1, int(i1)), (s2, int(i2)), float(population), float(r)))

  return bonds

def rgb(r,g,b):
  return 2**16 * r + 2**8 * g + b

def colour(pop):
  return "0x" + ("%02X" % (pop * 255)) *3

def clamp(x, a=0.0, b=1.0):
  if x < a: return a
  elif x > b: return b
  else: return x

def add_bonds(ions, castep_file, pop_tol=0.2, dist_tol=None):
  """
    Annotate collection of ions with bonding information from CASTEP run
  """
  
  bonds = parse_bonds(castep_file)

  if bonds == []:
    raise Exception("No bonds found")

  for ion in ions.ions:
    ion.bonds = []

  # Store all bonds, unduplicated
  ions.bonds = []

  for bond in bonds:
    (s1, i1), (s2, i2), pop, r = bond
    if pop_tol is not None and pop < pop_tol:
      continue
    if dist_tol is not None and r < dist_tol:
      continue
    ions.bonds.append(bond)
    
    ion1 = ions.get_species(s1, i1)
    ion2 = ions.get_species(s2, i2)

    d2, p2 = least_mirror(ion2.p, ion1.p, ions.basis, ions.lattice) # Mirror location of ion2 from ion1
    d2, p1 = least_mirror(ion1.p, ion2.p, ions.basis, ions.lattice) # Mirror location of ion1 from ion2
    
    ion1.bonds.append((ion2, p2, pop, r))
    ion2.bonds.append((ion1, p1, pop, r))

def bond_neighbours(ion, n=1, visited=None):
  """
    Find the nth nearest neighbours by bonding.
    Recursive.
  """
  if visited is None:
    visited = set([ion])

  rtn = set()
  for ion2, p, pop, r in ion.bonds:
    if ion2 not in visited:
      visited.add(ion2)
      if n == 1:
        rtn.add(ion2)
      else:
        rtn |= bond_neighbours(ion2, n-1, visited)
 
  return rtn

def find_common(ion1, ion2):
  """
    Find the commonly bonded ion between ion1 and ion2, for bond angle calcs
  """
  bonded1 = set([ion3 for ion3, p, _, _ in ion1.bonds])
  bonded2 = set([ion3 for ion3, p, _, _ in ion2.bonds])

  return set.intersection(bonded1,bonded2)

def bond_angle(ion1, ion2):
  common = find_common(ion1, ion2).pop()
  p1 = ion1.p
  _, p2 = least_mirror(common.p, p1)
  _, p3 = least_mirror(ion2.p, p2)
  bond1 = array(p2) - array(p1)
  bond2 = array(p2) - array(p3)
  return math.acos(dot(bond1, bond2)/math.sqrt(dot(bond1,bond1)*dot(bond2,bond2))) 

if __name__ == "__main__":
  """
    Given a .cell file and a .castep file, dump the most likely bonds to a file for plotting
  """
  
  c = castepy.Cell(open(sys.argv[1]).read())

  if 'jcoupling_site' in c.otherdict:
    s,i  = c.otherdict['jcoupling_site'].split()
    i = int(i)
    jc_ion = c.ions.get_species(s, i)

    print >>sys.stderr, jc_ion
    c.ions.translate_origin(jc_ion.p)
    c.ions.wrap_inside(-0.5, 0.5)
    print >>sys.stderr, jc_ion

  bonds = parse_bonds(open(sys.argv[2]).read())

  max_pop = max([pop for _, _, pop, _ in bonds])
  min_pop = 0.5

  for (s1, i1), (s2, i2), pop, r in bonds:
    ion1 = c.ions.get_species(s1, i1)
    ion2 = c.ions.get_species(s2, i2)

    if ion1.p[2] < -1.0/6 or ion1.p[2] > 1.0/6:
      #continue
      pass

    d2, p = ion.least_mirror(ion2.p, ion1.p)
    if pop > 0.2:
      print " ".join(map(str, ion1.p)), " ".join(map(str, p)), colour(clamp((pop-min_pop)/(max_pop-min_pop)))
