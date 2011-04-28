import math
from numpy import array, dot, add, subtract


def wrap(x, a, b):
  if x < b and x >= a:
    return x
  elif x < a:
    return x + b - a
  else:
    return x + a - b

def least_mirror(a, b, basis, lattice):
  # TOFIX: Fix assumption of fractional coordinates. Also, make sure if lattice is particularly thin in one direction it doesn't mess up.
  ap = dot(basis.T, a)
  a = dot(basis.T,array(a))
  b = dot(basis.T,array(b))
  min = None
  min_p = None

  for i in range(-1,2):
    for j in range(-1,2):
      for k in range(-1,2):
        ap = add(a, dot(lattice.T, (float(i), float(j), float(k))))
        r = subtract(ap, b)
        d = dot(r, r)

        if min is None or d < min:
          min = d
          min_p = ap

  return (min, min_p)

class Ion:
  """
    Generic ion. Can be annoated with other data.
  """
  
  def __init__(self, s, p):
    self.s = s
    self.p = p
    self.i = None

  def __str__(self):
    return "%s %s at %s" % (self.s, self.i, ", ".join(map(str,self.p)))

  def copy(self):
    rtn = Ion(str(self.s), tuple(self.p))
    rtn.i = int(i)
 
class Ions:
  def __init__(self):
    self.ions = []
    self.species_index = {}

  # Container emulation methods
  def __getitem__(self, idx):
    if type(idx) == tuple:
      s, i = idx
      return self.get_species(s, i)
    else:
      return self.ions[idx]

  def __len__(self):
    return len(self.ions)

  def __delitem__(self, idx):
    return self.remove_by_index(idx)

  def __cmp__(self, other):
    if isinstance(other, Ions):
      return cmp(self.ions, other.ions)
    else:
      return cmp(self.ions, other)

  def __iter__(self):
    return self.ions.__iter__()

  # Copying methods
  def copy_subset(self, subset):
    """
      Copy a subset of ions into a new Ions structure, updating bonds appropriately.
    """
    from copy import copy

    ion_map = {}
    for ion1 in subset:
      ion_new = Ion(copy(ion1.s), copy(ion1.p))
      ion_new.bonds = ion1.bonds
      self.add(ion_new)
      ion_map[ion1] = ion_new

    for ion1 in self:
      if hasattr(ion1, 'bonds'):
        new_bonds = []
        for ion2, p, pop, r in ion1.bonds:
          if ion2 in ion_map:
            new_bonds.append((ion_map[ion2], p, pop, r))
        ion1.bonds = new_bonds 

  # Methods to add and remove ions, keeping their internal indices up to date
  def add(self, ion):
    """
      Add an ion to the system.
    """
    
    self.ions.append(ion)

    if ion.s in self.species_index:
      self.species_index[ion.s].append(ion)
    else:
      self.species_index[ion.s] = [ion]

    ion.i = len(self.species_index[ion.s])
    ion.idx = len(self.ions)

    return (ion.s, ion.i)

  def remove(self, ion):
    """
      Remove ion
    """
    i = self.ions.index(ion)
    self.remove_by_index(i)

  def remove_by_index(self, i):
    """
      Remove ion with index i
    """
    ion = self.ions[i]
    del self.species_index[ion.s][ion.i-1]
    del self.ions[i]    
    
    self.regen_ion_index()

  def regen_ion_index(self):
    for species, ions in self.species_index.items():
      for i, ion in enumerate(ions):
        ion.i = i+1
    for idx, ion in enumerate(self.ions):
      ion.idx = idx + 1

  # Accessors by various indices
  def get_species(self, s, i=None):
    """
      Get all the atoms of a particular species or a particular ion by its species index
    """
    
    if i is None:
      return self.species_index[s]
    else:
      return self.species_index[s][i-1]

  def species(self):
    """
      Return species present, with count
    """
    
    return [(k, len(self.species_index[k])) for k in self.species_index.keys()]

  # Geometric routines
  def closest(self, q):
    """
      Find the ion closest to q, accounting for cyclic coordinates.
    """

    min_d2 = None
    min_ion = None
    min_p = None
     
    for ion in self.ions:
      d2,p = least_mirror(ion.p, q)

      if min_d2 is None or d2 < min_d2:
        min_d2 = d2
        min_ion = ion
        min_p = p

    return (min_ion, math.sqrt(min_d2), min_p)

  def neighbours(self, q, max_dist=None, above_index=0, species=None):
    """
      Return neighbours of q in distance order, for easy slicing
    """
    
    ions = []
    for i in range(above_index, len(self.ions)):
      ion = self.ions[i]
      d2, p = least_mirror(ion.p, q, self.basis, self.lattice)

      if (max_dist is None or d2 < max_dist**2) and (species is None or ion.s in species):
        ions.append((ion, math.sqrt(d2), p))
    
    return sorted(ions, key=lambda (ion,d,p): d)
#    return ions

  def translate_origin(self, p):
    """
      Translate all ions such that the origin is at p
    """

    for ion in self.ions:
      ion.p = (ion.p[0] - p[0],
               ion.p[1] - p[1],
               ion.p[2] - p[2],)

  def wrap_inside(self, a=0.0, b=1.0):
    """
      Wrap the ion positions to be inside the given unit cell
    """
    for ion in self.ions:
      ion.p = tuple([wrap(x, a, b) for x in ion.p])

  def remove_dupes(self, epsilon=1.0e-3):
    """
      Find and remove duplicate ions

    """

    remove = []
    for i1 in range(len(self.ions)):
      ion1 = self.ions[i1]
      overlap = False
      
      for i2 in range(i1+1, len(self.ions)):
        ion2 = self.ions[i2]
        d2, dp = least_mirror(ion1.p, ion2.p, self.basis, self.lattice)
        
        if d2 < epsilon*epsilon and ion1.s == ion2.s:
          print math.sqrt(d2), ion1, ion2
      
        if d2 < epsilon*epsilon: 
          overlap = True
    
      if overlap:
        remove.append(ion1)


    for ion in remove:
      self.remove(ion)

if __name__ == "__main__":
  """
    Tests.
  """

  ions = Ions()

  ions_test = []
  for i in range(10):
    a = Ion('Al', (float(i)*0.1+0.0009,0.0,0.0))
    b = Ion('Si', (float(i)*0.1,0.0,0.0))
    ions.add(a)
    ions.add(b)
    print a, b
    ions_test.append(a)
    ions_test.append(b)

  ions.remove_dupes()

  for ion in ions:
    print ion
