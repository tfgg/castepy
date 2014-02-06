import re
import sys
import numpy
from numpy import dot, array
import math

regex_block = re.compile("\s+Bond\s+Population\s+Length \(A\).*?\n[=]+\n(.*?)\n[=]+", re.M | re.S)
regex_line = re.compile("\s+([A-Za-z]+)\s+([0-9]+)\s+--\s+([A-Za-z]+)\s+([0-9]+)\s+([0-9\-\.]+)\s+([0-9\-\.]+)")

def parse_bonds_block(block):
  bonds = []

  for s1, i1, s2, i2, population, r in regex_line.findall(block):
    bonds.append(((s1, int(i1)), (s2, int(i2)), float(population), float(r)))

  return bonds

def parse_bonds(castep_file):
  """
    Parse bonding information from .castep file
  """

  bond_blocks = regex_block.findall(castep_file)

  for block in bond_blocks:
    bonds = parse_bonds_block(block)
    yield bonds

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

  for atom in ions:
    atom.bonds = []

  # Store all bonds, unduplicated
  ions.bonds = []

  for bond in bonds:
    (s1, i1), (s2, i2), pop, r = bond
    if pop_tol is not None and pop < pop_tol:
      continue
    if dist_tol is not None and r < dist_tol:
      continue
    ions.bonds.append(bond)
    
    ion1 = ions.species_index[s1][i1-1]
    ion2 = ions.species_index[s2][i2-1]

    _, p2 = ions.least_mirror(ion2.position, ion1.position) # Mirror location of ion2 from ion1
    _, p1 = ions.least_mirror(ion1.position, ion2.position) # Mirror location of ion1 from ion2
    
    ion1.bonds.append((ion2, ion1.position, pop, r))
    ion2.bonds.append((ion1, ion2.position, pop, r))

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

def bond_angle(ion1, ion2, ions):
  common = find_common(ion1, ion2).pop()
  p1 = ion1.p
  _, p2 = least_mirror(common.p, p1, ions.basis, ions.lattice)
  _, p3 = least_mirror(ion2.p, p2, ions.basis, ions.lattice)

  bond1 = array(p2) - array(p1)
  bond2 = array(p2) - array(p3)

  # print math.sqrt(dot(bond1, bond1)), math.sqrt(dot(bond2, bond2))

  return math.acos(dot(bond1, bond2)/math.sqrt(dot(bond1,bond1)*dot(bond2,bond2))) 


class BondsResult(object):
  def __init__(self, bonds, tol=0.25):
    self.bonds = [bond for bond in bonds if bond[2] >= tol]
    self._build_index()

  @classmethod
  def load(klass, castep_file, tol=0.25):
    for bonds in parse_bonds(castep_file):
      yield BondsResult(bonds, tol)

  def _build_index(self):
    self.index = {}

    for idx1, idx2, population, r in self.bonds:
      if idx1 not in self.index:
        self.index[idx1] = {}
        
      self.index[idx1][idx2] = (population, r)
      
      if idx2 not in self.index:
        self.index[idx2] = {}
        
      self.index[idx2][idx1] = (population, r)

  def common(self, idx1, idx2):
    bonded1 = set(self.index[idx1].keys())
    bonded2 = set(self.index[idx2].keys())

    return bonded1 & bonded2

  def __str__(self):
    out = []
    for idx1, idx2, population, r in self.bonds:
      out.append("{}{} -{:.2f}A-> {}{} ({:.2f})".format(idx1[0],idx1[1],r,idx2[0],idx2[1],population))
    return "\n".join(out)

