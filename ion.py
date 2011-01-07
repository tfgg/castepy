import math
import numpy

class Basis:
  def __init__(self, a, b, c):
    self.basis = [a,b,c]
    self.matrix = numpy.matrix(self.basis)
    self.AA = self.matrix.transpose() * self.matrix

  def cart(self, v):
    return numpy.dot(self.matrix, v)

Basis.cartesian = Basis((1.0,0.0,0.0), (0.1,0.0,0.0), (0.0,0.1,0.0))

def wrap(x, a, b):
  if x < b and x >= a:
    return x
  elif x < a:
    return x + b - a
  else:
    return x + a - b

def least_mirror(a, b, basis=Basis.cartesian):
  ap = a
  a = numpy.matrix(a).transpose()
  b = numpy.matrix(b).transpose()
  counter = 0
  min = 0.0
  min_p = None
  for i in range(-1,2):
    for j in range(-1,2):
      for k in range(-1,2):
        counter += 1
        r =  a - b + numpy.matrix((float(i), float(j), float(k))).transpose()
        d = float(r.transpose() * basis.AA * r)

        p = (ap[0]+float(i), ap[1]+float(j), ap[2]+float(k))
        if counter == 1:
          min = d
          min_p = p
        elif counter >= 2:
          if d < min:
            min =  d
            min_p = p

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
 
class Ions:
  def __init__(self):
    self.ions = []
    self.species_index = {}

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

  def neighbours(self, q, max_dist=None, above_index=0):
    """
      Return neighbours of q in distance order, for easy slicing
    """
    
    ions = []
    for i in range(above_index, len(self.ions)):
      ion = self.ions[i]
      d2, p = least_mirror(ion.p, q)

      if max_dist is None or d2 < max_dist**2:
        ions.append((ion, math.sqrt(d2), p))
    
#    return sorted(ions, key=lambda (ion,d,p): d)
    return ions

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
        d = least_mirror(ion1.p, ion2.p)
      
        if d < epsilon: 
          overlap = True
    
      if overlap:
        remove.append(ion1)

    for ion in remove:
      self.remove(ion)

  def bonds(self, castep_file, max_dist=0.001):
    import bonds

    bs = bonds.parse_bonds(castep_file)
    
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

  for ion in ions.ions:
    print ion
