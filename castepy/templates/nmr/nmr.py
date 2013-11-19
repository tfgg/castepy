import sys, os, argparse
import shutil
import random

import castepy.settings as settings
from castepy.input import cell, parameters, pot
from castepy.calc import CastepCalc
from castepy.util import calc_from_path

nmr_path = os.path.join(settings.CASTEPY_ROOT, "templates/nmr")

merge_cell = cell.Cell(open(os.path.join(nmr_path, "nmr.cell")).read())
params = parameters.Parameters(open(os.path.join(nmr_path, "nmr.param")).read())

import argparse

parser = argparse.ArgumentParser(description='Create a CASTEP NMR calculation.')

parser.add_argument('source', help='A cell file to build the calculation from.')
parser.add_argument('target_dir', help='A directory to build the calculation in.')
parser.add_argument('-n', '--num_cores', type=int, help='Number of cores to use.', default=32)
parser.add_argument('-q', '--queue', type=str, help='SGE queue to use.', default="parallel.q")
parser.add_argument('-x', '--xc_functional', help='The XC functional to use', default="PBE")
parser.add_argument('-c', '--cut_off_energy', type=int, help='The cut-off energy to use (Rydberg)', default=50)
parser.add_argument('-e', '--efg', action="store_const", const=True, default=False, help="Only do an EFG calculation")
parser.add_argument('-p', '--ncp_pot', action="store_const", const=True, default=False, help="Use norm-conserving pseudopotentials")
parser.add_argument('-r', '--rel_pot', action="store_const", const=True, default=False, help="Use relativistic pseudopotentials")

def make_command(args):
  a = parser.parse_args(args)

  make(a.source,
       a.target_dir,
       num_cores=a.num_cores,
       queue=a.queue,
       xc_functional=a.xc_functional,
       cut_off_energy=a.cut_off_energy,
       ncp_pot=a.ncp_pot,
       rel_pot=a.rel_pot,
       efg=False)

def make(source, target_dir, target_name=None, num_cores=32, queue="parallel.q", xc_functional="pbe", cut_off_energy=50, ncp_pot=False, rel_pot=False, efg=False, c=None, **kwargs):

  source_dir, source_name = calc_from_path(source)
  calc = CastepCalc(source_dir, source_name)
  
  xc_functional = xc_functional.lower()

  if c is None:
    c = cell.Cell(calc.cell_file)

  c.other += merge_cell.other
  c.blocks.update(merge_cell.blocks)

  if ncp_pot:
    if xc_functional == 'pbe':
      _, required_files = pot.add_potentials(settings.NCP_PSPOT_PBE_DIR, None, c, rel_pot)
    elif xc_functional == 'lda':
      _, required_files = pot.add_potentials(settings.NCP_PSPOT_LDA_DIR, None, c, rel_pot)
    else:
      raise Exception("Cannot use XC functional %s with NCPs" % xc_functional)

    pot.link_files(required_files, target_dir)
  else:
    print rel_pot
    pot.add_potentials_usp(c, rel_pot)

  if target_name is None:
    target_name = source_name

  cell_target = os.path.join(target_dir, "%s.cell" % target_name)
  param_target = os.path.join(target_dir, "%s.param" % target_name)
  sh_target = os.path.join(target_dir, "%s.sh" % target_name)

  sh_context = {'seedname': target_name,
                'num_cores': num_cores,
                'h_vmem': float(num_cores)/8 * 23,
                'queue': queue,
                'CASTEPY_ROOT': settings.CASTEPY_ROOT,
                'USER_EMAIL': settings.USER_EMAIL,
                }

  sh_source = open(os.path.join(nmr_path, "nmr.sh")).read()
  sh_target_file = open(sh_target, "w+")
  param_target_file = open(param_target, "w+")

  params.xc_functional[0] = xc_functional
  params.cut_off_energy[0] = cut_off_energy

  if efg:
    params.magres_task = "efg"
  else:
    params.magres_task = "nmr"

  print >>sh_target_file, sh_source % sh_context
  print >>param_target_file, params
  
  cell_out = open(cell_target, "w+")

  print >>cell_out, c

  sh_target_file.close()

if __name__ == "__main__":
  make_command(sys.argv[1:])

