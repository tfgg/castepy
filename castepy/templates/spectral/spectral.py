import sys, os
import shutil

from castepy import castepy
from castepy import constraint
from castepy import cell
from castepy import calc
from castepy.util import calc_from_path, path

relax_path = path("templates/spectral")
merge_cell = cell.Cell(open(os.path.join(relax_path, "spectral.cell")).read())

def make(source_dir, source_name, target_dir):
  cal = calc.CastepCalc(source_dir, source_name)
  c = cell.Cell(cal.cell_file)

  c.other += merge_cell.other

  target_cell = os.path.join(target_dir, "%s.cell" % source_name)
  target_param = os.path.join(target_dir, "%s.param" % source_name)
  target_sh = os.path.join(target_dir, "%s.sh" % source_name)

  shutil.copyfile(os.path.join(relax_path, "spectral.param"), target_param)
  shutil.copyfile(os.path.join(relax_path, "spectral.sh"), target_sh)

  cell_out = open(target_cell, "w+")

  print >>cell_out, str(c)

if __name__ == "__main__":
  source_calc = str(sys.argv[1])
  source_dir, source_name = calc_from_path(source_calc)
  target_dir = str(sys.argv[2])

  make(source_dir, source_name, target_dir)

