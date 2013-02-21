import sys, os
import shutil
import re
import random

import castepy.settings as settings

from castepy import castepy, cell, pot
from castepy.calc import CastepCalc
from castepy.util import calc_from_path

from castepy.templates.submission_scripts import get_submission_script

jc_path = os.path.join(settings.CASTEPY_ROOT, "templates/jc")

merge_cell = cell.Cell(open(os.path.join(jc_path, "jc.cell")).read())

regex_species = re.compile('([A-Za-z]+)([0-9]+)')

def make(source_dir, source_name, target_dir, target_name=None, jc_s=None, jc_i=None, rel_pot=False, c=None, **kwargs):
  calc = CastepCalc(source_dir, source_name)

  if c is None:
    c = cell.Cell(calc.cell_file)

  _, required_files= pot.add_potentials(settings.NCP_PSPOT_DIR, None, c, rel_pot)
  pot.link_files(required_files, target_dir)

  c.other = []

  if jc_s is None:
    # Let's first see if we can guess the species from the target directory.
    # I usually name mine e.g. Pb17, so it can guess from that
    species_matches = regex_species.findall(target_dir) 

    if species_matches:
      jc_s = species_matches[0][0]
      jc_i = int(species_matches[0][1])
      jsiteraw = raw_input("Specify the j-coupling site (%s %d): " % (jc_s, jc_i))

      if jsiteraw:
        j_site = jsiteraw.split()
        jc_s = j_site[0]
        jc_i = int(j_site[1])
    else:
      jsiteraw = raw_input("Specify the j-coupling site: ")

      j_site = jsiteraw.split()
      jc_s = j_site[0]
      jc_i = int(j_site[1])

  if jc_s is not None:
    jc_ion = c.ions.get_species(jc_s, jc_i)
  
    c.other.append("jcoupling_site: %s %d" % (jc_s, jc_i))
    c.otherdict['jcoupling_site'] = "%s %d" % (jc_s, jc_i)

  #c.jcoupling_shift_origin()
  c.ions.translate_origin([0.001, 0.001, 0.001])

  if 'KPOINTS_LIST' in c.blocks:
    del c.blocks['KPOINTS_LIST']
  
  c.other += merge_cell.other

  if target_name is None:
    target_name = source_name

  cell_target = os.path.join(target_dir, "%s.cell" % target_name)
  param_target = os.path.join(target_dir, "%s.param" % target_name)
  sh_target = os.path.join(target_dir, "%s.sh" % target_name)

  shutil.copyfile(os.path.join(jc_path, "jc.param"), param_target)

  if 'num_cores' in kwargs:
    num_cores = kwargs['num_cores']
  else:
    num_cores = 32

  #queue = random.choice(["parallel.q", "parallel.q", "long.q"])
  queue = "parallel.q"
  
  sh_context = {'seedname': target_name,
                'CASTEPY_ROOT': settings.CASTEPY_ROOT,
                'USER_EMAIL': settings.USER_EMAIL,
                'num_cores': num_cores,
                'h_vmem': float(num_cores)/8 * 23,
                'queue': queue,
                'code': 'castep-jc'}

  print sh_context

  sh_source = get_submission_script()
  sh_target_file = open(sh_target, "w+")

  print >>sh_target_file, sh_source % sh_context

  sh_target_file.close()

  cell_out = open(cell_target, "w+")

  print >>cell_out, str(c)

if __name__ == "__main__":
  dir, name = calc_from_path(sys.argv[1])
  target_dir = str(sys.argv[2])

  make(dir, name, target_dir)

