# -*- coding: utf-8 -*-
import re
import math
from castepy import Cell
import numpy

def tensor_properties(matrix):
  m = numpy.mat(numpy.reshape(matrix, (3,3)))

  m_sym = (m + m.H)/2.0
  m_asym = (m - m.H)/2.0
  eval, evec = numpy.linalg.eig(m_sym)

  prop = {}
  prop['iso'] = sum(eval)/3.0  
  prop['aniso'] = eval[2] - (eval[0] + eval[1])/2.0
  prop['asym'] = (eval[1] - eval[0]) / (eval[2] - prop['iso'])

  return prop

class Magres:
  def __init__(self, magres_file=None):
    if magres_file is not None:
      self.parse(magres_file)

  def parse(self, magres_file):
    """
      Parse a CASTEP .magres file for total tensors.
    """
    
    atom_regex = re.compile("============\nAtom: ([A-Za-z]+)\s+([0-9]+)\n============\n([^=]+)\n", re.M | re.S)
    shielding_tensor_regex = re.compile("\s{0,}(.*?) Shielding Tensor\n\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+")

    jc_tensor_regex = re.compile("\s{0,}J-coupling (.*?)\n\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+")

    efg_tensor_regex = re.compile("\s{0,}(.*?) tensor\n\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\n\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+")

    atoms = atom_regex.findall(magres_file)

    self.ms = False
    self.efg = False
    self.jc = False

    self.atoms = {}

    for atom in atoms:
      index = atom[0], int(atom[1])

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

    for (s, i), magres in self.atoms.items():
      ion = ions.get_species(s, i)

      ion.magres = {}

      if 'ms' in magres:
        ion.magres['ms'] = magres['ms']['TOTAL']

      if 'efg' in magres:
        ion.magres['efg'] = magres['efg']['TOTAL']
      
      if 'jc' in magres:
        if 'jc' not in ion.magres:
          ion.magres['jc'] = {}
          ion.magres['jc_prop'] = {}
        ion.magres['jc'][(jc_ion_s, jc_ion_i)] = magres['jc']['Total']
        ion.magres['jc_prop'][(jc_ion_s, jc_ion_i)] = tensor_properties(magres['jc']['Total'])

class NMRResult:
  nmr_regex = re.compile(r"  \|\s+Chemical Shielding.*?\n.*?\n(.*?)\n(.*?)\n(.*?)\n\s+\n", re.M | re.S);
  entry_row_regex = re.compile(r"(.*?)\n")
  entry_regex = re.compile(r"([A-Za-z0-9.\-\\+\*]+)\s+")
  heading_group_regex = re.compile(r"([A-Z][^\|]+?)  ")
  heading_regex = re.compile(r"\s+([^\|]+?) ")

  class NoNMRResult(Exception): pass
  class NoNMRIons(Exception): pass
  
  def __init__(self, castep_file=None):
    self.ions = None
    self.groups = None # Available properties per ion
    
    if castep_file is not None:
      self.parse(castep_file)

  def parse(self, castep_file):
    search_results = self.nmr_regex.findall(castep_file)

    if search_results is [] or len(search_results) == 0:
      raise self.NoNMRResult()

    search_result = search_results[len(search_results) - 1]

    heading_groups = self.heading_group_regex.findall(search_result[0])
    headings = self.heading_regex.findall(search_result[1])

    entry_rows = self.entry_row_regex.findall(search_result[2])

    if entry_rows is None:
      raise NoNMRIons()
    
    #self.groups, _ = zip(*sorted(self.entry_regex.groupindex.items(), key=lambda v: v[1]))
    clean_brackets = re.compile(r"\(.*?\)")
    self.groups = [heading.lower() for heading in headings]
    self.groups.append("perturb")
    
    self.ions = []
    for entry_row in entry_rows:
      is_perturb = ""
      if entry_row.find("|** ") != -1:
        entry_row = entry_row.replace("|** ", "", 1)
        is_perturb = "**"
      
      entries = self.entry_regex.findall(entry_row)
      entries.append(is_perturb)
      # Stop at a blank line
      if len(entries) == 1: break

      self.ions.append(dict(zip(self.groups, entries)))
    
    return self.ions
  
  def get_property(self, p, species):
    prop = []

    for ion in self.ions:
      if species is None or ion['species'] == species:
        prop.append(ion[p])
    
    return prop

  def csv(self, species, number=None, sortgroup="tot(hz)", limit=10):
    s = "#" + ", ".join(self.groups) + "\n"

    class CExc(Exception): pass

    def ion_filter(ion): 
        return (species is None or species == ion['species']) and (number is None or number==ion['ion'])

    sorted_ions = sorted(self.ions, key=lambda x: abs(float(x[sortgroup])), reverse=True)
    for ion in filter(ion_filter, sorted_ions)[:limit]:
      try:
        ps = []
        for group in self.groups:
          if group in ion:
            ps.append(ion[group])
          else:
            raise CExc()
        s += ", ".join(ps) + "\n"
      except CExc:
        pass

    return s

  def annotate(self, ions):
    for nmr_ion in self.ions:
      ion = ions.get_species(nmr_ion['species'], int(nmr_ion['ion']))
      ion.nmr = nmr_ion

class JNMRResult(NMRResult):
    nmr_regex = re.compile(r"  \|\s+Isotropic J-coupling.*?\n.*?\n(.*?)\n(.*?)\n(.*?)\n\s+\n", re.M | re.S);

class JNMRResultAniso(NMRResult):    
    nmr_regex = re.compile(r"  \|\s+Anisotropic J-coupling.*?\n.*?\n(.*?)\n(.*?)\n(.*?)\n\s+\n", re.M | re.S);
 
if __name__ == "__main__":
  import os, sys

  magres_file = open(sys.argv[1]).read()
  cell_file = open(sys.argv[2]).read()

  m = Magres()
  m.parse(magres_file)

  c = Cell(cell_file)
  m.annotate(c.ions)

  for ion in c.ions:
    if hasattr(ion, 'magres'):
      print ion.s, ion.i, ion.magres

  sys.exit(1)

  file_path = sys.argv[1]
  prop = "iso"
  species = None
  
  if len(sys.argv) > 2:
    prop = str(sys.argv[2])

  if len(sys.argv) > 3:
    species = str(sys.argv[3])

  castep_file = open(file_path, "r").read()

  nmr_result = NMRResult(castep_file)
  
  if prop in nmr_result.groups:
    print " ".join(nmr_result.get_property(prop, species))
  elif prop == "all":
    if species is None:
      print nmr_result.ions
    else:
      print [ion for ion in nmr_result.ions if ion['species'] == species]
  elif prop == "csv":
    print nmr_result.csv(species)
  else:
    print "Available ion properties:", ", ".join(nmr_result.groups)
