# -*- coding: utf-8 -*-
import sys
import re
import math
import numpy

from cell import Cell
from magres.format import MagresFile

from magres_constants import gamma_common, efg_to_Cq

def tensor_properties(matrix):
  m = numpy.mat(numpy.reshape(matrix, (3,3)))

  m_sym = (m + m.H)/2.0
  m_asym = (m - m.H)/2.0
#  eval, evec = numpy.linalg.eig(m_sym)

  prop = {}
  prop['iso'] = numpy.trace(m_sym)/3.0  
#  prop['aniso'] = eval[2] - (eval[0] + eval[1])/2.0
# prop['asym'] = (eval[1] - eval[0]) / (eval[2] - prop['iso'])

  return prop

class DictAttrAccessor:
  def __init__(self, d):
    self.d = d

  def __getattr__(self, key):
    if key not in self.d:
      raise AttributeError
    else:
      if type(self.d[key]) == dict:
        return DictAttrAccessor(self.d[key])
      else:
        return self.d[key]

class MagresResult(object):
  def __init__(self, magres_file=None):
    """
      Load new .magres format file into dictionary structure.
    """

    if type(magres_file) == MagresFile:
      self.magres_file = magres_file
    else:
      self.magres_file = MagresFile(magres_file)

  def __getattr__(self, key):
    if 'magres' not in self.magres_file.data_dict:
      raise AttributeError(key)

    d = self.magres_file.data_dict['magres']

    if key not in d:
      raise AttributeError(key)
    else:
      if type(d[key]) == dict:
        return DictAttrAccessor(d[key])
      else:
        return d[key]

  def annotate(self, ions):
    """
      Given the corresponding ions structure, annotate with magres data.
    """

    try:
      for s1, i1, s2, i2, K_tensor in self.isc:
        ion1 = ions.get_species(s1, i1)

        if not hasattr(ion1, 'magres'):
          ion1.magres = {}

        if 'isc' not in ion1.magres:
          ion1.magres['isc'] = {}

        ion1.magres['isc'][(s2, i2)] = numpy.asarray(K_tensor)
    except AttributeError:
      pass

    try:
      for s, i, efg_tensor in self.efg:
        ion = ions.get_species(s, i)

        if not hasattr(ion1, 'magres'):
          ion.magres = {}

        if 'efg' not in ion1.magres:
          ion1.magres['efg'] = {}

        ion1.magres['efg'] = numpy.asarray(efg_tensor)
    except AttributeError:
      pass

class OldMagresResult:
  def __init__(self, magres_file=None):
    if magres_file is not None:
      self.parse(magres_file)

  def parse(self, magres_file):
    """
      Parse a CASTEP .magres file for total tensors.
    """
    #print >>sys.stderr,"Parsing magres"
    atom_regex = re.compile("============\nAtom: ([A-Za-z\:0-9]+)\s+([0-9]+)\n============\n([^=]+)\n", re.M | re.S)
    shielding_tensor_regex = re.compile("\s{0,}(.*?) Shielding Tensor\n\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+")

    jc_tensor_regex = re.compile("\s{0,}J-coupling (.*?)\n\n\s+([0-9eE\.\-]+)\s+([0-9eE\.\-]+)\s+([0-9eE\.\-]+)\n\s+([0-9eE\.\-]+)\s+([0-9eE\.\-]+)\s+([0-9eE\.\-]+)\n\s+([0-9eE\.\-]+)\s+([0-9eE\.\-]+)\s+([0-9eE\.\-]+)\s+")

    efg_tensor_regex = re.compile("\s{0,}(.*?) tensor\n\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+")

    atoms = atom_regex.findall(magres_file)

    #shielding_tensors = shielding_tensor_regex.findall(magres_file)
    #efg_tensors = efg_tensor_regex.findall(magres_file)
    #jc_tensors = jc_tensor_regex.findall(magres_file)
    #print >>sys.stderr,shielding_tensors
    #print >>sys.stderr,efg_tensors
    #print >>sys.stderr,jc_tensors

    self.ms = False
    self.efg = False
    self.jc = False

    self.atoms = {}

    #print >>sys.stderr,"Building atoms"
    for atom in atoms:
      index = atom[0].split(":")[0], int(atom[1])

      if index not in self.atoms:
        self.atoms[index] = {}

      shielding_tensors = shielding_tensor_regex.findall(atom[2])
      if len(shielding_tensors) != 0:
        self.ms = True
        self.atoms[index]['ms'] = {}
        for tensor in shielding_tensors:
          self.atoms[index]['ms'][tensor[0]] = map(float, tensor[1:])

      efg_tensors = efg_tensor_regex.findall(atom[2])
      if len(efg_tensors) != 0:
        self.efg = True
        self.atoms[index]['efg'] = {}
        for tensor in efg_tensors:
          self.atoms[index]['efg'][tensor[0]] = map(float, tensor[1:])

      jc_tensors = jc_tensor_regex.findall(atom[2])
      if len(jc_tensors) != 0:
        self.jc = True
        self.atoms[index]['jc']  = {}
        for tensor in jc_tensors:
          self.atoms[index]['jc'][tensor[0]] = map(float, tensor[1:])
          

  def annotate(self, ions):
    """
      Given an ion collection, add the nmr information to each ion object.
    """
    print >>sys.stderr,"Annotating"
    if self.jc:
      # If doing J-coupling, find the perturbing atom. It should be missing from our magres atoms list.
      # The perturbing atom is actually in the .magres file but the regex doesn't pick it up.
      jc_ion_s = None
      jc_ion_i = None
      for ion in ions:
        found = False
        for s, i in self.atoms:
          if ion.s == s and ion.i == i:
            found = True
            break
        if not found:
          jc_ion_s = ion.s
          jc_ion_i = ion.i

      self.jc_ion = (jc_ion_s, jc_ion_i)

    for (s, i), magres in self.atoms.items():
      ion = ions.get_species(s, i)

      ion.magres = {}

      if 'ms' in magres:
        ion.magres['ms'] = numpy.reshape(magres['ms']['TOTAL'], (3,3))
         
      if 'efg' in magres:
        ion.magres['efg'] = numpy.reshape(magres['efg']['TOTAL'], (3,3))
        ion.magres['Cq'] = efg_to_Cq(ion.magres['efg'], ion.s)

      if 'jc' in magres:
        if 'jc' not in ion.magres:
          ion.magres['isc'] = {}
          ion.magres['jc'] = {}
          ion.magres['jc_prop'] = {}
        J_tensor = [x * gamma_common[s] * gamma_common[jc_ion_s] * 1.05457148e-15 / (2.0 * math.pi) for x in magres['jc']['Total']]
        ion.magres['isc'][(jc_ion_s, jc_ion_i)] = magres['jc']['Total']
        ion.magres['jc'][(jc_ion_s, jc_ion_i)] = J_tensor
        ion.magres['jc_prop'][(jc_ion_s, jc_ion_i)] = tensor_properties(J_tensor)

