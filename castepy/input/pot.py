# -*- coding: utf-8 -*-
# Add required potentials to given cell file. Optionally links files into directory containing cell file

import os
import sys
import re

from castepy import settings
from castepy.input.cell import Cell
from castepy.constants import Z 

from castepy.input.otfg7 import otfg as otfg7
from castepy.input.otfg8 import otfg as otfg8

otfgs = {7: otfg7,
         8: otfg8,}

def add_potentials_asc(c, xc="pbe", rel=False):
  potentials = [PspASC(s, xc, rel) for s in c.ions.species_index]

  c.blocks['SPECIES_POT'] = ["{} {}".format(pot.s, pot) for pot in potentials] 
  
  return potentials

def add_potentials_usp(cell_file, type=None, otfg_version=8, otfg_patch=None):
  if cell_file.__class__ != Cell:
    c = Cell(open(cell_file).read())
  else:
    c = cell_file
  
  species_pot = []
  for s in c.ions.species_index:
    if otfg_patch is None or s not in otfg_patch:
      otfg_string = otfgs[otfg_version][s]
    else:
      otfg_string = otfg_patch[s]

    pot = PspOtfg(s, otfg_string)

    if type is not None:
      if type == "zora":
        if rel and Z[s] >= 19:
          pot.flags[type] = None
        else:
          pot.flags['schro'] = None
      else:
        pot.flags[type] = None
        
    species_pot.append("{} {}".format(s, pot))

  c.blocks['SPECIES_POT'] = species_pot

class PspASC(object):
  pspot_dir = {'pbe': settings.NCP_PSPOT_PBE_DIR,
               'lda': settings.NCP_PSPOT_LDA_DIR,}

  def __init__(self, s, xc="pbe", rel=False):
    self.s = s
    self.xc = xc
    self.rel = rel

  def required_files(self):
    dir = self.pspot_dir[self.xc] 

    if self.rel:
      rtn = [(os.path.join(dir, "{}_POT_REL.ASC.DAT".format(self.s)), "{}_POT.ASC.DAT".format(self.s)),
             (os.path.join(dir, "{}_AEPS_REL.DAT".format(self.s)), "{}_AEPS.DAT".format(self.s)),]

    else:
      rtn = [(os.path.join(dir, "{}_POT.ASC.DAT".format(self.s)), "{}_POT.ASC.DAT".format(self.s)),
             (os.path.join(dir, "{}_AEPS.DAT".format(self.s)), "{}_AEPS.DAT".format(self.s)),]
      
    if not all(os.path.isfile(path) for path, _ in rtn):
      if self.rel:
        rtn = [(os.path.join(dir, "{}_POT.ASC.DAT".format(self.s)), "{}_POT.ASC.DAT".format(self.s)),
               (os.path.join(dir, "{}_AEPS.DAT".format(self.s)), "{}_AEPS.DAT".format(self.s)),]

        if not all(os.path.isfile(path) for path, _ in rtn):
          raise Exception("Could not find fallback non-rel pseudpotential files for {} (xc={}, rel={})".format(self.s, self.xc, self.rel))

      else:
        raise Exception("Could not find non-rel pseudpotential files for {} (xc={}, rel={})".format(self.s, self.xc, self.rel))

    return rtn

  def link_files(self, target_dir, replace=False):
    paths = self.required_files()

    for path, target_name in paths:
      path = os.path.abspath(path)
      target = os.path.join(target_dir, target_name)

      if replace or not os.path.isfile(target):
        if replace:
          os.unlink(target)

        os.symlink(path, target)

  def __str__(self):
    return "{0}_POT.ASC.DAT".format(self.s)


class PspOtfg(object):
  def __init__(self, species, otfg_str):
    self.species = species
    self.l_local = None
    self.rc_local = None
    self.rc_other = None
    self.rc_aug = None
    self.projectors = []
    self.flags = {}

    self.parse(otfg_str)

  def parse(self, otfg_str):
    pipesplit = otfg_str.split('|')

    if len(pipesplit) == 8:
      self.l_local = int(pipesplit[0])
      self.rc_local = float(pipesplit[1])
      self.rc_other = float(pipesplit[2])
      self.rc_aug = float(pipesplit[3])
    elif len(pipesplit) == 6:
      self.l_local = int(pipesplit[0])
      self.rc_local = float(pipesplit[1])
      self.rc_other = None
      self.rc_aug = None
    else:
      raise Exception("Unknown pipe section")

    self.energy_test = map(float, pipesplit[-4:-1])

    self.projectors = re.findall("(.*?)([\(\[{]|$)", pipesplit[-1])[0][0].split(":")

    if '(' in otfg_str:
      flags = otfg_str[otfg_str.index('(')+1:otfg_str.index(')')].split(',')

      for flag in flags:
        if '=' in flag:
          key, val = flag.split('=')
          self.flags[key] = val
        else:
          self.flags[key] = None

    if '{' in otfg_str:
      self.config_gen = otfg_str[otfg_str.index('{')+1:otfg_str.index('}')].split(',')
    else:
      self.config_gen = None
    
    if '[' in otfg_str:
      self.config_test = otfg_str[otfg_str.index('[')+1:otfg_str.index(']')].split(',')
    else:
      self.config_test = None

  def __str__(self):
    out = []

    out.append("{}|".format(self.l_local))
    out.append("{}|".format(self.rc_local))

    if self.rc_other:
      out.append("{}|".format(self.rc_other))

    if self.rc_aug:
      out.append("{}|".format(self.rc_aug))
    
    out.append("{}|{}|{}|".format(*self.energy_test))

    out.append(":".join(self.projectors))

    if self.config_gen:
      out.append("{{{}}}".format(",".join(self.config_gen)))
   
    if self.flags:
      out.append("(")
      flags = []
      for key, value in self.flags.items():
        if value:
          flags.append("{}={}".format(key, value))
        else:
          flags.append(key)

      out.append(",".join(flags))
      out.append(")")
    
    if self.config_test:
      out.append("[{}]".format(",".join(self.config_test)))

    return "".join(out)


if __name__ == "__main__":
  for s, otfg_str in otfgs[8].items():
    print s, otfg_str

    psp = PspOtfg(s, otfg_str)

    print "  ", psp

