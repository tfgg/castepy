import sys, os
import shutil

from castepy import castepy, pot, cell
from castepy.calc import CastepCalc
from castepy.util import calc_from_path

pot_dir = "/home/green/scratch/ncp_pspot/"
nmr_path = "/home/green/pylib/castepy/templates/nmr"

merge_cell = cell.Cell(open(os.path.join(nmr_path, "nmr.cell")).read())

def make(source_dir, source_name, target_dir, target_name=None, c=None):
  calc = CastepCalc(source_dir, source_name)
  
  if c is None:
    c = cell.Cell(calc.cell_file)

  c.other += merge_cell.other

  if target_name is None:
    target_name = source_name

  cell_target = os.path.join(target_dir, "%s.cell" % target_name)
  param_target = os.path.join(target_dir, "%s.param" % target_name)
  sh_target = os.path.join(target_dir, "%s.sh" % target_name)

  sh_context = {'seedname': target_name, }
  sh_source = open(os.path.join(nmr_path, "nmr.sh")).read()
  sh_target_file = open(sh_target, "w+")

  print >>sh_target_file, sh_source % sh_context
  shutil.copyfile(os.path.join(nmr_path, "nmr.param"), param_target)
  shutil.copyfile(os.path.join(nmr_path, "nmr.sh"), sh_target)

  cell_out = open(cell_target, "w+")

  print >>cell_out, str(c)

  sh_target_file.close()

if __name__ == "__main__":
  dir, name = calc_from_path(sys.argv[1])
  target_dir = str(sys.argv[2])

  make(dir, name, target_dir)

