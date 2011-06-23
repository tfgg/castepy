import sys, os
import shutil

from castepy import castepy, pot, cell
from castepy.calc import CastepCalc
from castepy.util import calc_from_path

pot_dir = "/home/green/scratch/ncp_pspot/"
jc_path = "/home/green/pylib/castepy/templates/jc"

merge_cell = cell.Cell(open(os.path.join(jc_path, "jc.cell")).read())

def make(source_dir, source_name, target_dir, target_name=None, jc_s=None, jc_i=None):
  calc = CastepCalc(source_dir, source_name)
  c = cell.Cell(calc.cell_file)

  _, required_files= pot.add_potentials(pot_dir, None, c)
  pot.link_files(required_files, target_dir)

  if jc_s is not None:
    jc_ion = c.ions.get_species(jc_s, jc_i)
  
    c.other.append("jcoupling_site: %s %d" % (jc_s, jc_i))
    c.otherdict['jcoupling_site'] = "%s %d" % (jc_s, jc_i)

  c.jcoupling_shift_origin()
  if 'KPOINTS_LIST' in c.blocks:
    del c.blocks['KPOINTS_LIST']
  
  c.other += merge_cell.other

  if target_name is None:
    target_name = source_name

  cell_target = os.path.join(target_dir, "%s.cell" % target_name)
  param_target = os.path.join(target_dir, "%s.param" % target_name)
  sh_target = os.path.join(target_dir, "%s.sh" % target_name)

  shutil.copyfile(os.path.join(jc_path, "jc.param"), param_target)

  sh_context = {'seedname': target_name,}
  sh_source = open(os.path.join(jc_path, "jc.sh")).read()
  sh_target_file = open(sh_target, "w+")
  print >>sh_target_file, sh_source % sh_context
  sh_target_file.close()

  cell_out = open(cell_target, "w+")

  print >>cell_out, str(c)

if __name__ == "__main__":
  dir, name = calc_from_path(sys.argv[1])
  target_dir = str(sys.argv[2])

  make(dir, name, target_dir)

