import sys, os
import shutil
import random

import castepy.settings as settings
from castepy.input import cell
from castepy.calc import CastepCalc
from castepy.util import calc_from_path

psptest_path = os.path.join(settings.CASTEPY_ROOT, "templates/psptest")

merge_cell = cell.Cell(open(os.path.join(psptest_path, "psptest.cell")).read())

def make(source_ascpot, source_aeps, target_dir, **kwargs):
  cell = merge_cell

  s = os.path.split(source_ascpot)[1].split('_')[0]

  cell.ions[0].s = s

  target_name = s

  dir_ncp = os.path.join(target_dir, 'ncp/')
  dir_usp = os.path.join(target_dir, 'usp/')

  if not os.path.isdir(dir_ncp):
    os.mkdir(dir_ncp)
  if not os.path.isdir(dir_usp):
    os.mkdir(dir_usp)

  cell_target = os.path.join(dir_usp, "%s.cell" % target_name)
  param_target = os.path.join(dir_usp, "%s.param" % target_name)
  sh_target = os.path.join(dir_usp, "%s.sh" % target_name)

  #if 'num_cores' in kwargs:
  #  num_cores = kwargs['num_cores']
  #else:
  num_cores = 8

  queue = "parallel.q,shortpara.q"

  sh_context = {'seedname': target_name,
                'num_cores': num_cores,
                'h_vmem': float(num_cores)/8 * 23,
                'queue': queue,
                'CASTEPY_ROOT': settings.CASTEPY_ROOT,
                'USER_EMAIL': settings.USER_EMAIL,
                }

  sh_source = open(os.path.join(psptest_path, "psptest.sh")).read()

  print >>open(sh_target, "w+"), sh_source % sh_context
  shutil.copyfile(os.path.join(psptest_path, "psptest.param"), param_target)
  print >>open(cell_target, "w+"), str(cell)
  
  cell_target = os.path.join(dir_ncp, "%s.cell" % target_name)
  param_target = os.path.join(dir_ncp, "%s.param" % target_name)
  sh_target = os.path.join(dir_ncp, "%s.sh" % target_name)
  ascpot_target = os.path.join(dir_ncp, "%s_POT.ASC.DAT" % s)
  aeps_target = os.path.join(dir_ncp, "%s_AEPS.DAT" % s)
  
  shutil.copyfile(source_ascpot, ascpot_target)
  shutil.copyfile(source_aeps, aeps_target)

  cell.blocks['SPECIES_POT'] = ["%s %s_POT.ASC.DAT" % (s, s)]

  print >>open(sh_target, "w+"), sh_source % sh_context
  shutil.copyfile(os.path.join(psptest_path, "psptest.param"), param_target)
  print >>open(cell_target, "w+"), str(cell)

if __name__ == "__main__":
  dir, name = calc_from_path(sys.argv[1])
  target_dir = str(sys.argv[2])

  make(dir, name, target_dir)

