# -*- coding: utf-8 -*-
# Add required potentials to given cell file. Optionally links files into directory containing cell file

import os
import sys
import re

from castepy.input.cell import Cell

def add_potentials(pot_dir, dir_path, cell_file, rel=False):
  if cell_file.__class__ != Cell:
    c = Cell(open(cell_file).read())
  else:
    c = cell_file

  species_pot_string = "%s %s_POT.ASC.DAT"
  species_pot = []
  required_files = set()
  for s, n in c.ions.species():
      species_pot.append(species_pot_string % (s, s))

      # Check for relativistic potential
      if rel and os.path.isfile(os.path.join(pot_dir, "%s_AEPS_REL.DAT" % s)):
        required_files.add((os.path.join(pot_dir, "%s_AEPS_REL.DAT" % s), "%s_AEPS.DAT" % s))
      elif os.path.isfile(os.path.join(pot_dir, "%s_AEPS.DAT" % s)):
        required_files.add((os.path.join(pot_dir, "%s_AEPS.DAT" % s), "%s_AEPS.DAT" % s))

      if rel and os.path.isfile(os.path.join(pot_dir, "%s_POT_REL.ASC.DAT" % s)):
        required_files.add((os.path.join(pot_dir, "%s_POT_REL.ASC.DAT" % s), "%s_POT.ASC.DAT" % s))
      else:
        required_files.add((os.path.join(pot_dir, "%s_POT.ASC.DAT" % s), "%s_POT.ASC.DAT" % s))

  c.blocks['SPECIES_POT'] = species_pot
  return (c, required_files)

def add_potentials_usp(cell_file, rel=False, type='schro'):
  if cell_file.__class__ != Cell:
    c = Cell(open(cell_file).read())
  else:
    c = cell_file
 
  def make_lab(usp_s, type):
    if '(' in usp_s:
      return usp_s.replace(')', ',%s)' % type)
    else:
      return usp_s.replace('[', '(%s)[' % type)
  
  if rel:
    species_pot = []
    for s, n in c.ions.species():
      species_pot.append("%s %s" % (s, make_lab(otfg[s], type)))
  else:
    species_pot = []
    for s, n in c.ions.species():
      species_pot.append("%s %s" % (s, make_lab(otfg[s], type)))

  c.blocks['SPECIES_POT'] = species_pot

  return (c, [])

def link_files(required_files, dir_path):
  for f, target_name in required_files:
    if not os.path.isfile(f):
      raise Exception("Required potential file \"%s\" doesn't exist." % f)
    else:
      f = os.path.abspath(f)            
      target = os.path.join(dir_path, target_name)

      if not os.path.isfile(target):
        os.symlink(f, target)

class PspOtfg(object):
  def __init__(self, otfg_str):
    self.l_local = None
    self.rc_local = None
    self.rc_other = None
    self.rc_aug = None
    self.projectors = []
    self.flags = []
    self.flags_dict = {}

    self.parse(otfg_str)

  def parse(self, otfg_str):
    pipesplit = otfg_str.split('|')

    self.l_local = int(pipesplit[0])
    self.rc_local = float(pipesplit[1])
    self.rc_other = float(pipesplit[2])
    self.rc_aug = float(pipesplit[3])

    # projstr = pipesplit[-1][:pipesplit.index('(')].split(':')

    if '(' in otfg_str:
      self.flags = otfg_str[otfg_str.index('(')+1:otfg_str.index(')')].split(',')

      for flag in self.flags:
        if '=' in flag:
          key, val = flag.split('=')
          self.flags_dict[key] = val

otfg = {'H':  "1|0.8|3.675|7.35|11.025|10UU(qc=6.4)[]",
      'He':  "1|0.8|0.8|0.6|14.7|16.5|20|10UU(qc=7)[]",
      'Li':  "1|1.2|11|13.2|15|10U:20UU(qc=5.5)[]",
      'Be':  "1|1.4|1.4|0.7|10.6|12|13.7|10U:20U[]",
       'B':  "2|1.4|9.187|11.025|13.965|20UU:21UU(qc=5.5)[]",
       'C':  "2|1.4|9.187|11.025|12.862|20UU:21UU(qc=6)[]",
       'N':  "2|1.5|11.025|12.862|14.7|20UU:21UU(qc=6)[]",
       'O':  "2|1.3|16.537|18.375|20.212|20UU:21UU(qc=7.5)[]",
       'F':  "2|1.4|16.537|18.375|20.212|20UU:21UU(qc=7.5)[]",
      'Ne':  "2|1.6|1.6|1.2|12.1|13.2|14.7|20UU:21UU(qc=6)[]",
      'Na':  "2|1.3|1.3|1|11.8|13.6|15.3|20U=-2.07:30U=-0.105:21U=-1.06U=+0.25[]",
      'Mg':  "2|1.6|2|1.4|6|7|8|30NH:21U:31UU:32LGG(qc=4.5)[]",
      'Al':  "2|2|3.675|5.512|7.717|30UU:31UU:32LGG[]",
      'Si':  "2|1.8|3.675|5.512|7.35|30UU:31UU:32LGG[]",
       'P':  "2|1.8|3.675|5.512|6.982|30UU:31UU:32LGG[]",
       'S':  "2|1.7|1.7|1.3|5.9|9.2|11|30UU:31UU:32LGG[]",
      'Cl':  "2|1.7|5.88|7.35|9.187|30UU:31UU:32LGG[]",
      'Ar':  "2|1.7|1.7|1|11|12|13|30UU:31UU[]",
       'K':  "2|1.8|1.8|1.6|11|14.7|16.7|30U:40UU:31UU(qc=5.5)[]",
      'Ca':  "3|1.6|2|1.4|7.5|9.2|10.3|30U=-1.72:40U=-0.14:31U=-1.03U=+0.25:32U=+0U=+1[]",
      'Sc':  "3|1.8|1.8|1.6|9.6|10.8|11.7|30U=-2.01:40U=-0.16:31U=-1.235U=+0.25:32U=-0.125U=+0.25[]",
      'Ti':  "3|1.8|1.8|1.5|10|11|12.2|30U=-2.29:40U=-0.17:31U=-1.425U=+0.5:32U=-0.165U=+0.15[]",
       'V':  "3|2|2|1.4|10|13|15|30U=-3.06:40U=-0.465:31U=-2.105U=+0.1:32U=-1.15U=+0.1[]",
      'Cr':  "3|1.8|1.8|1.8|10|12.1|14.7|30U=-2.965:40U=-0.255:31U=-1.92U=+0.5:32U=-0.335U=+0.25[]",
      'Mn':  "3|2.3|2.3|1.5|7.4|8.8|10|40N:32UU:41N{4s0.75,4p0.25}(qc=4.5,q0=3)[]",
      'Fe':  "1|2|2.2|1.5|9.6|10.7|12.1|40UU:32U2U2{4s1.75}[]",
      'Co':  "3|2.5|2.5|1.5|5.9|7.7|10|40UU:32UU:41UU{4s1.95,4p0.05}(qc=4)[]",
      'Ni':  "-1|2|2|1.5|7.4|10|12|40U=-0.25U=+0.25:41U=-0.075U=+0.25:32U=-0.39U=+0.25[]",
      'Cu':  "3|2.2|2.15|1.5|9.2|12.9|14.7|40UU:41UU:32UU{4s0.5,4p0.001}[4s0.5,4p0.001]",
      'Zn':  "3|2|2|1|10.8|11.5|12.5|40UU:41UU:32UU(qc=6)[]",
      'Ga':  "3|2|2|1.5|9.9|11|12.4|40U=-0.335U=+0.25:41U=-0.1U=+0.25:32U=-0.715U=+0.25[]",
      'Ge':  "2|2.3|2.3|1.5|4.4|6|9|40U=-0.44U=+0.25:41U=-0.15U=+0.25[]",
      'As':  "2|1.6|1.6|0.9|6|7.3|9.9|40U=-0.54U=+0.5:41U=-0.195U=+0.25[]",
      'Se':  "2|1.6|1.6|1.3|8.5|10|11.4|40U=-0.645U=+0.25:41U=-0.245U=+0.25[]",
      'Br':  "2|2|2|1.4|5.6|6.6|8.8|40U=-0.74U=+0.25:41U=-0.295U=+0.25[]",
      'Kr':  "2|1.9|1.9|1.3|9|10|11|40UU:41UU[]",
      'Rb':  "2|2.5|2.5|2.1|5.5|6.6|8.1|40U:50U+0U+0.125:41UU(qc=3.5)[]",
      'Sr':  "3|2|2|1.2|7.4|9.2|11|40U:50U:41UU:42UU[]",
       'Y':  "3|2|2|2|8.5|10|11.1|40U:50U:41UU:42UU[]",
      'Zr':  "3|2.1|2.1|1.05|8.5|10|11.4|40U=-2.005:50U=-0.17:41U=-1.195U=+0.1:42U=-0.135U=+0.25[]",
      'Nb':  "3|2.2|2.2|1|7.7|8.8|10|40U=-2.145:50U=-0.145:41U=-1.27U=+0.25:42U=-0.1U=+0[]",
      'Mo':  "3|2|2|2|8.9|10.1|11.7|40U=-2.365:50U=-0.15:41U=-1.415U=+0.25:42U=-0.14U=+0.25[]",
      'Ru':  "3|2|2|1.5|9.6|10.6|11.7|40U=-2.93:50U=-0.2:41U=-1.825U=+0.25:42U=-0.285U=+0.25[]",
      'Rh':  "1|2.2|2.2|1.5|9|10|11.7|50U=-0.17:42U=-0.225U=+0.25[]",
      'Pd':  "3|2|2|1.5|10|12.1|14|40U:50U:41UU:42UU{5s0.05}(qc=5.5)[]",
      'Ag':  "1|2.2|2.3|1.6|9|11|12|50U=-0.185U=+0.4:42U=-0.3U=+0[]",
      'Cd':  "1|2.2|2.2|1.6|8.7|9.6|10.7|50U+0U+0.1:42UU(qc=5,q0=4)[]",
      'In':  "3|2.3|2.3|1.6|9|10.5|12|50UU:51UU:42UU[]",
      'Sn':  "2|2|2|1.6|9.6|10.8|11.7|50U=-0.395U=+0.25:51U=-0.14U=+0.25[]",
      'Sb':  "2|2|2|1.6|4|7|8|50U=-0.48U=+0.25:51U=-0.185U=+0.25[]",
      'Te':  "2|2.2|2.2|1.6|5.2|6.4|8.4|50U=-0.565U+0.5:51U=-0.225U=+0.25[]",
       'I':  "2|2|2|1.6|6|7.3|9.9|50U=-0.65U=+0:51U=-0.265U=+0[]",
      'Xe':  "2|2|2|1.6|9|10|11|50UU:51UU[]",
      'Cs':  "2|2.7|2.7|1.6|4.4|5.9|7.4|50U:60U+0U+0.125:51UU(qc=3.5)[]",
      'Ba':  "2|3|2.9|2.2|6.4|8.1|9|50U:60UU:51U2.5U2.5(qc=3.5)[]",
      'La':  "2|2|2|1.4|8|12|13|50N:60NH:51UU:52LGG:43U1.6+0U1.6+0.1{5d0.9,4f0.1}(qc=6)[]",
      'Pr':  "2|2.1|2|1.3|12.1|14.7|18.4|50U=-1.44:60U=-0.13:51U=-0.79U=+0.25:43U=-0.055U=+0.25[]",
      'Sm':  "2|2.1|1.9|1.3|12|13.2|14.7|50U=-1.595:60U=-0.135:51U=-0.855U=+0.25:43U=-0.1U=+0.25[]",
      'Eu':  "2|2.1|2|1.3|13.5|14.7|15.5|50U1.6:60U1.6:51U1.8U1.8:43UU(qc=6)[]",
      'Gd':  "2|2.1|2|1.3|13.5|14.7|15.5|50U1.6:60U1.6:51U1.8U1.8:43UU:52UU(qc=6)[]",
      'Dy':  "2|2.1|2|1.3|16.9|18.8|21.4|50U:60U:51UU:43UU(qc=6.5)[]",
      'Yb':  "2|1.8|2|1.5|12.5|13.5|14.7|50U1.6:60U1.6:51U1.8U1.8:43UU{4f13}(qc=6)[4f13]",
      'Lu':  "2|2.1|2.1|2.1|8|9.2|10.3|50U:60U:51UU:52UU[]",
      'Hf':  "1|2.4|2.4|1.2|6.6|8.5|11.3|60U=-0.195U=+1.75:52U=-0.105U=+0[]",
      'Ta':  "1|2.4|2.4|1.2|7|8.8|10|60U=-0.2U=+1.75:52U=-0.14U=+0[]",
       'W':  "3|2.1|2.1|2.1|8.5|9.6|10.6|50U:60U:51UU:52UU[]",
      'Re':  "3|2.1|2.1|2.1|9|10.7|11|50U=-3.14:60U=-0.225:51U=-1.735U=+0.25:52U=-0.205U=+0.25[]",
      'Os':  "3|2|2|1.8|9.2|10.7|11.4|50U=-3.375:60U=-0.235:51U=-1.875U=+0.2:52U=-0.24U=+0.25[]",
      'Ir':  "3|2|2|1.8|10.5|11.4|12|50U:60U:51UU:52UU(qc=5.5)[]",
      'Pt':  "1|2.3|2.4|1|8.4|9.2|10.7|60U=-0.22:52U=-0.235U=+0[]",
      'Au':  "3|2|2|1.8|11.4|12.5|13.3|50U:60U:51UU:52UU(qc=5.5)[]",
      'Hg':  "1|2.2|2.2|1.7|11.8|13.6|15.3|60UU:61P:52UU[]",
      'Tl':  "3|2.4|2.4|1.9|8.5|9.6|11|60UU:61U+0U+0.5:52UU(qc=4.5)[]",
      'Pb':  "3|2.4|2.35|1.6|9.2|12.9|16.5|60UU:61UU:52UU[]",
      'Bi':  "2|2.1|2.1|1.6|7|9.2|11|60U=-0.54U=+0.25:61U=-0.175U=+0.25[]",
      'U':   "2|2.1|2|1.4|12.5|14|16|60U:70U:61UU:53UU:62P(qc=6)[]",
      'Pu':  "2|2.1|2.2|1.3|12.1|14.7|16.7|60U:70U:61UU:53UU(qc=6)[]",
      'Am':  "2|2.1|2.1|1.5|14.7|16.2|18.4|60U:70U:61UU:53UU(qc=6)[]",
      'Cm':  "2|2.1|2.2|1.6|16.9|18.8|20.4|60U:70U:61UU:53UU:62L(qc=6)[]",}

