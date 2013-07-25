import sys, os
import shutil
import re
import random
import pipes
import itertools

import castepy.settings as settings

from castepy.input import cell, pot, parameters
from castepy.calc import CastepCalc
from castepy.utils import calc_from_path

from castepy.templates.submission_scripts import get_submission_script

jc_path = os.path.join(settings.CASTEPY_ROOT, "templates/jc")

merge_cell = cell.Cell(open(os.path.join(jc_path, "jc.cell")).read())
params = parameters.Parameters(open(os.path.join(jc_path, "jc.param")).read())

regex_species = re.compile('([A-Za-z]+)([0-9]+)')

import argparse

parser = argparse.ArgumentParser(description='Create a CASTEP J-coupling calculation.')
parser.add_argument('source', help='A cell file to build the calculation from.')
parser.add_argument('target_dir', help='A directory to build the calculation in.')
parser.add_argument('-n', '--num_cores', type=int, help='Number of cores to use.', default=32)
parser.add_argument('-q', '--queue', type=str, help='SGE queue to use.', default="parallel.q")
parser.add_argument('-s', '--site', help='Target J-coupling site(s), separated by commas.', type=str)
parser.add_argument('-r', '--rel_pot', action="store_const", help='Use relativity', default=False, const=True)
parser.add_argument('-u', '--usp_pot', action="store_const", help='Use ultrasoft potentials', default=False, const=True)
parser.add_argument('-x', '--xc_functional', help='The XC functional(s) to use, separated by commas.', default="PBE")
parser.add_argument('-c', '--cut_off_energy', type=str, help='The cut-off energy(s) to use (Rydberg), separated by commas.', default="80")

def make_command(args):
  a = parser.parse_args(args)

  print a.__dict__

  sites = []
  if a.site is not None:
    for site in a.site.split(","):
      sites.append(regex_species.findall(site)[0])
  else:
    sites = [None]

  cut_off_energies = map(int,a.cut_off_energy.split(","))
  xc_functionals = [s.lower() for s in a.xc_functional.split(",")]

  param_prod = list(itertools.product(sites, cut_off_energies,xc_functionals))

  print param_prod

  for site, cut_off_energy,xc_functional in param_prod:
    if len(param_prod) == 1:
      target_dir = a.target_dir
    else:
      if site is not None:
        target_dir = os.path.join(a.target_dir, "%s-%dry-%s" % ("".join(site), cut_off_energy, xc_functional))
      else:
        target_dir = os.path.join(a.target_dir, "%dry-%s" % (cut_off_energy, xc_functional))
     
      if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    if site is not None:
      jc_s, jc_i = site
      jc_i = int(jc_i)
    else:
      jc_s = None
      jc_i = None

    make(a.source,
         target_dir,
         num_cores=a.num_cores,
         jc_s=jc_s,
         jc_i=jc_i,
         rel_pot=a.rel_pot,
         usp_pot=a.usp_pot,
         xc_functional=xc_functional,
         cut_off_energy=cut_off_energy,
         queue=a.queue)

def make(source, target_dir, num_cores=32, target_name=None, jc_s=None, jc_i=None, rel_pot=False, xc_functional='pbe', cut_off_energy=80, usp_pot=False, c=None, queue="parallel.q", **kwargs):

  source_dir, source_name = calc_from_path(source)
  calc = CastepCalc(source_dir, source_name)

  xc_functional = xc_functional.lower()

  if c is None:
    c = cell.Cell(calc.cell_file)

  if usp_pot:
    pot.add_potentials_usp(c)
  else:
    if xc_functional == 'pbe':
      _, required_files = pot.add_potentials(settings.NCP_PSPOT_PBE_DIR, None, c, rel_pot)
    elif xc_functional == 'lda':
      _, required_files = pot.add_potentials(settings.NCP_PSPOT_LDA_DIR, None, c, rel_pot)
    else:
      raise Exception("Cannot use XC functional %s with NCPs" % xc_functional)

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

  c.ions.translate_origin([0.001, 0.001, 0.001])

  if 'KPOINTS_LIST' in c.blocks:
    del c.blocks['KPOINTS_LIST']
  
  c.other += merge_cell.other

  if target_name is None:
    target_name = source_name

  cell_target = os.path.join(target_dir, "%s.cell" % target_name)
  param_target = os.path.join(target_dir, "%s.param" % target_name)
  sh_target = os.path.join(target_dir, "%s.sh" % target_name)

  params.xc_functional[0] = xc_functional
  params.cut_off_energy[0] = cut_off_energy

  if usp_pot:
    code = "castep-jcusp.mpi"
  else:
    code = "castep-jc"

  sh_context = {'seedname': pipes.quote(target_name),
                'CASTEPY_ROOT': settings.CASTEPY_ROOT,
                'USER_EMAIL': settings.USER_EMAIL,
                'num_cores': num_cores,
                'h_vmem': float(num_cores)/8 * 23,
                'queue': queue,
                'code': code}

  sh_source = get_submission_script()
  sh_target_file = open(sh_target, "w+")
  param_target_file = open(param_target, "w+")

  print >>sh_target_file, sh_source % sh_context
  print >>param_target_file, params

  sh_target_file.close()
  param_target_file.close()

  cell_target_file = open(cell_target, "w+")

  print >>cell_target_file, c

if __name__ == "__main__":
  make_command(sys.argv[1:])

