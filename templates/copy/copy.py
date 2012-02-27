import sys, os
import shutil

from castepy import castepy
from castepy import constraint
from castepy import cell
from castepy.calc import CastepCalc
from castepy.util import calc_from_path

def make(source_dir, source_name, target_dir):
  calc = CastepCalc(source_dir, source_name)

  target_cell = os.path.join(target_dir, "%s.cell" % source_name)
  target_param = os.path.join(target_dir, "%s.param" % source_name)
  target_sh = os.path.join(target_dir, "%s.sh" % source_name)
  
  shutil.copyfile(os.path.join(source_dir, "%s.sh" % source_name), target_sh)

  # Find .DAT files for J-coupling to link, maybe redo this so it uses pot.linkfiles
  for f in os.listdir(source_dir):
    if '.DAT' in f:
      source = os.path.abspath(os.path.join(source_dir, f))
      target = os.path.join(target_dir, f)
      
      if not os.path.isfile(target):
        os.symlink(source, target)

  cell_out = open(target_cell, "w+")
  print >>cell_out, calc.cell_file
  param_out = open(target_param, "w+")
  print >>param_out, calc.param_file

if __name__ == "__main__":
  source_calc = str(sys.argv[1])
  dir, name = calc_from_path(source_calc)
  target_dir = str(sys.argv[2])

  make(dir, name, target_dir)

