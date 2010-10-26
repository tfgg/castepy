# -*- coding: utf-8 -*-
import re

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
    search_result = self.nmr_regex.search(castep_file)

    if search_result is None:
      raise NoNMRResult()

    heading_groups = self.heading_group_regex.findall(search_result.group(1))
    headings = self.heading_regex.findall(search_result.group(2))

    entry_rows = self.entry_row_regex.findall(search_result.group(3))

    if entry_rows is None:
      raise NoNMRIons()
    
    #self.groups, _ = zip(*sorted(self.entry_regex.groupindex.items(), key=lambda v: v[1]))
    clean_brackets = re.compile(r"\(.*?\)")
    self.groups = [re.sub(r"\(.*?\)", "", heading.lower()) for heading in headings]
    
    self.ions = []
    for entry_row in entry_rows:
      entry_row = entry_row.replace("** ", "")
      entries = self.entry_regex.findall(entry_row)
      
      # Stop at a blank line
      if len(entries) == 0: break

      self.ions.append(dict(zip(self.groups, entries)))
    
    return self.ions
  
  def get_property(self, p, species):
    prop = []

    for ion in self.ions:
      if species is None or ion['species'] == species:
        prop.append(ion[p])
    
    return prop

  def csv(self, species):
    s = "#" + ", ".join(self.groups) + "\n"

    class CExc(Exception): pass

    for ion in self.ions:
      try:
        if species is None or species == ion['species']:
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

class JNMRResult(NMRResult):
    nmr_regex = re.compile(r"  \|\s+Isotropic J-coupling.*?\n.*?\n(.*?)\n(.*?)\n(.*?)\n\s+\n", re.M | re.S);
    
if __name__ == "__main__":
  import os, sys

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
