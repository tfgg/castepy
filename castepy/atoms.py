import sys,os
import math
import numpy
import re

from atom import Atom, AtomImage

class ListPropertyView(list):
  """
    Allows property accessors on lists of objects. E.g.

    x = [A(1), A(2), A(3)]
    x.a = [1,2,3]

    if A(a) is an object that stores a in self.a
  """

  def mean(self, *args, **kwargs):
    """
      Take the mean of the properties.
    """
    return numpy.mean([x for x in self], *args, **kwargs) 

  def __getattr__(self, prop):
    if any([hasattr(x, prop) for x in self]):
      return ListPropertyView([getattr(x, prop, None) for x in self])
    else:
      raise AttributeError("{} not present".format(prop))

def insideout():
  """
    Generator to count up in positive numbers and down in negative numbers
  """

  yield 0

  i = 1

  while True:
    yield i
    yield -i
    i += 1

class LabelNotFound(Exception):
  pass

class SpeciesNotFound(Exception):
  pass

class AtomNotFound(Exception):
  pass

class AtomsView(object):
  """
    A container for a collection of atoms with an optional lattice.
  """
  ViewType = None

  def __init__(self, atoms=None, lattice=None):
    if atoms is not None:
      self.atoms = atoms
    else:
      self.atoms = []

    if lattice is not None:
      self.lattice = lattice
    else:
      self.lattice = None

    self.label_index = {}
    self.species_index = {}

    self._build_index()

  def add(self, atoms):
    """
      Add an extra atom or list of atoms.
    """

    try:
      # Try to iterate and append
      for atom in atoms:
        self.atoms.append(atom)
    except TypeError:
      # Not iterable, assume atom type
      self.atoms.append(atoms)

    self._build_index()

  def _build_index(self):
    self.label_index.clear()
    self.species_index.clear()

    for atom in self.atoms:
      if atom.label in self.label_index:
        self.label_index[atom.label].append(atom)
      else:
        self.label_index[atom.label] = [atom]
      
      if atom.species in self.species_index:
        self.species_index[atom.species].append(atom)
      else:
        self.species_index[atom.species] = [atom]

  def get(self, species, index):
    return self.species_index[species][index-1]

  def label(self, label):
    """
      Return a AtomsView containing only atoms of the specified label.

      >>> atoms.label("C1")
    """
    if type(label) != list:
      label = [label]
      
    rtn_atoms = []
    for l in label:
      if l in self.label_index:
        rtn_atoms += self.label_index[l]
    return self.ViewType(rtn_atoms, self.lattice)

  def species(self, species):
    """
      Return a AtomsView containing only atoms of the specified species.

      >>> atoms.species('C')
    """
    if type(species) != list:
      species = [species]
      
    rtn_atoms = []
    for s in species:
      if s in self.species_index:
        rtn_atoms += self.species_index[s]
    return self.ViewType(rtn_atoms, self.lattice)

  def within(self, pos, max_dr):
    """
      Return all atoms within max_dr Angstroms of pos, including all images.

      >>> atoms.within(p, 5.0)
    """

    if type(pos) is Atom:
      pos = pos.position

    atoms = []

    for atom in self.atoms:
      if type(atom) == Atom:
        images = self._all_images_within(atom.position, pos, max_dr)

        for image_dist, image_pos in images:
          if image_dist <= max_dr:
            atoms.append(AtomImage(atom, image_pos))
      elif type(atom) == AtomImage:
        if atom.dist(pos) <= max_dr:
          atoms.append(atom)

    return self.ViewType(atoms, self.lattice)

  def least_mirror(self, a, b):
    """
      Give the closest periodic image of a to b given the current lattice.
    """
    min = None
    min_p = None

    for i in range(-1,2):
      for j in range(-1,2):
        for k in range(-1,2):
          ap = numpy.add(a, numpy.dot(self.lattice.T, (float(i), float(j), float(k))))
          r = numpy.subtract(ap, b)
          d = numpy.dot(r, r)

          if min is None or d < min:
            min = d
            min_p = ap

    return (math.sqrt(min), min_p)

  def _all_images_within(self, a, b, r):
    """
      Give all images of a to b within distance r.
    """

    images = []

    for i in insideout():
      any_j = False

      for j in insideout():
        any_k = False

        for k in insideout():
          R = numpy.dot(self.lattice.T, numpy.array([float(i), float(j), float(k)]))
          
          if numpy.dot(a+R-b,a+R-b) > r*r:
            if k < 0:
              break
            else:
              continue

          any_k = True
          any_j = True
      
          ap = numpy.add(a, R)
          dr = numpy.subtract(ap, b)
          d = numpy.dot(dr, dr)

          images.append((math.sqrt(d), ap))

        if not any_k and j < 0:
          break

      if not any_j and i < 0:
        break

    images = sorted(images, key=lambda (d,p): d)

    return images

  re_species_index = re.compile('([A-Za-z]+)([0-9]+)')

  def __getattribute__(self, attr_name):
    try:
      return object.__getattribute__(self, attr_name)
    except AttributeError:
      try:
        s, i = self.re_species_index.findall(attr_name)[0]
        return self.species_index[s][int(i)-1]
      except:
        return getattr(ListPropertyView(self.atoms), attr_name)

  def __getitem__(self, idx):
    try:
      s, i = idx
      return self.species_index[s][i-1]
    except:
      return self.atoms[idx]

  def __iter__(self):
    return self.atoms.__iter__()

  def __len__(self):
    return len(self.atoms)

  def __add__(self, b):
    # Shouldn't typecheck here. Replace with ducktyping.
    if type(b) is self.ViewType and (self.lattice == b.lattice).all():
      new_atoms = set(self.atoms).union(set(b.atoms))

      return self.ViewType(list(new_atoms), self.lattice)

    elif type(b) is Atom:
      new_atoms = set(self.atoms + [b])
      
      return self.ViewType(list(new_atoms), self.lattice)

  def __radd__(self, b):
    # Shouldn't typecheck here. Replace with ducktyping.
    if type(b) is Atom:
      new_atoms = set(self.atoms + [b])
      
      return self.ViewType(list(new_atoms), self.lattice)

AtomsView.ViewType = AtomsView

class Atoms(AtomsView):
  def __init__(self, *args, **kwargs):
    super(Atoms, self).__init__(*args, **kwargs)

