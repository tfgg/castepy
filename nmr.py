# -*- coding: utf-8 -*-
import sys
import re
import math
import numpy

from cell import Cell
import format
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

class NewMagres:
  def __init__(self, magres_file=None):
    """
      Load new .magres format file into dictionary structure.
    """

    self.data = format.load_magres(magres_file) 
    self.atoms = format.load_into_dict_new(self.data)

  def annotate(self, ions):
    """
      Given the corresponding ions structure, annotate.
    """
    if 'jc' in self.atoms:
      for s1, i1 in self.atoms['jc']:
        ion1 = ions.get_species(s1, i1)
        if not hasattr('magres', ion1):
          ion1.magres = {}

        if 'jc' in ion1.magres:
          ion1.magres['jc'] += self.atoms['jc'][(s1, i1)]
        else:
          ion1.magres['jc'] = self.atoms['jc'][(s1, i1)]

        ion1.magres['jc_iso'] = dict([(si, numpy.trace(J)) for si, J in ion1.magres['jc'].items()])
          

    for (s, i) in self.atoms.items():
      ion = ions.get_species(s, i)

      ion.magres = self.atoms[(s,i)]

      #if 'jc' in magres:
      #  if 'jc' not in ion.magres:
      #    ion.magres['isc'] = {}
      #    ion.magres['jc'] = {}
      #    ion.magres['jc_prop'] = {}
      #  J_tensor = [x * gamma_common[s] * gamma_common[jc_ion_s] * 1.05457148e-15 / (2.0 * math.pi) for x in magres['jc']['Total']]
      #  ion.magres['isc'][(jc_ion_s, jc_ion_i)] = magres['jc']['Total']
      #  ion.magres['jc'][(jc_ion_s, jc_ion_i)] = J_tensor
      #  ion.magres['jc_prop'][(jc_ion_s, jc_ion_i)] = tensor_properties(J_tensor)

class Magres:
  def __init__(self, magres_file=None):
    if magres_file is not None:
      self.parse(magres_file)

  def parse(self, magres_file):
    """
      Parse a CASTEP .magres file for total tensors.
    """
    print >>sys.stderr,"Parsing magres"
    atom_regex = re.compile("============\nAtom: ([A-Za-z\:0-9]+)\s+([0-9]+)\n============\n([^=]+)\n", re.M | re.S)
    shielding_tensor_regex = re.compile("\s{0,}(.*?) Shielding Tensor\n\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+")

    jc_tensor_regex = re.compile("\s{0,}J-coupling (.*?)\n\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+")

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

    print >>sys.stderr,"Building atoms"
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

