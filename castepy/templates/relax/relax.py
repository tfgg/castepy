import sys, os, argparse
import shutil

from castepy.input import constraint, parameters, cell
from castepy import calc
from castepy.utils import calc_from_path
import castepy.settings as settings

relax_path = os.path.join(settings.CASTEPY_ROOT, "templates/relax")
merge_cell = cell.Cell(open(os.path.join(relax_path, "relax.cell")).read())
params = parameters.Parameters(open(os.path.join(nmr_path, "nmr.param")).read())

parser.add_argument('source', help='A cell file to build the calculation from.')
parser.add_argument('target_dir', help='A directory to build the calculation in.')
parser.add_argument('-n', '--num_cores', type=int, help='Number of cores to use.', default=32)
parser.add_argument('-q', '--queue', type=str, help='SGE queue to use.', default="parallel.q")
parser.add_argument('-x', '--xc_functional', help='The XC functional to use', default="PBE")
parser.add_argument('-c', '--cut_off_energy', type=int, help='The cut-off energy to use (Rydberg)', default=50)
parser.add_argument('-s', '--species', type=str, help='Comma separated list of species to relax. ', default="all")
parser.add_argument('--relax_cell', action="store_const", const=True, default=False, help="Relax cell lattice vectors.")

def make_command(args):
  a = parser.parse_args(args)

  if a.species == "all":
    species = None
  else:
    species = a.species.split(",")

  make(a.source,
       a.target_dir,
       relax_species=species,
       relax_cell=a.relax_cell,
       num_cores=a.num_cores,
       queue=a.queue,
       xc_functional=a.xc_functional,
       cut_off_energy=a.cut_off_energy)
       
def make(source, target_dir, target_name=None, relax_species=["H"], relax_cell=False, num_cores=32, queue="parallel.q", xc_functional="pbe", cut_off_energy=50):
  source_dir, source_name = calc_from_path(source)

  xc_functional = xc_functional.lower()
  
  cal = calc.CastepCalc(source_dir, source_name)
  c = cell.Cell(cal.cell_file)
  if relax_species is None:
    filter = lambda ion: False
  else:
    filter = lambda ion: ion.s not in relax_species

  c.ions.remove_dupes(epsilon=0.1) # Remove duplicate atoms closer than 0.1 angstrom
  constraint.add_constraints(c, filter)
  
  c.other += merge_cell.other
  
  if target_name is None:
    target_name = source_name

  if 'num_cores' in kwargs:
    num_cores = kwargs['num_cores']
  else:
    num_cores = 32

  #if num_cores == 32:
  #  queue = "long.q"
  #else:
  queue = "parallel.q"

  target_cell = os.path.join(target_dir, "%s.cell" % source_name)
  target_param = os.path.join(target_dir, "%s.param" % source_name)
  target_sh = os.path.join(target_dir, "%s.sh" % source_name)

  sh_context = {'seedname': target_name,
                'num_cores': num_cores,
                'h_vmem': float(num_cores)/8 * 23,
                'queue': queue,}

  sh_source = open(os.path.join(relax_path, "relax.sh")).read()
  sh_target_file = open(target_sh, "w+")
  
  print >>sh_target_file, sh_source % sh_context

  shutil.copyfile(os.path.join(relax_path, "relax.param"), target_param)
  #shutil.copyfile(os.path.join(relax_path, "relax.sh"), target_sh)

  cell_out = open(target_cell, "w+")

  print >>cell_out, str(c)

if __name__ == "__main__":
  source_calc = str(sys.argv[1])
  source_dir, source_name = calc_from_path(source_calc)
  target_dir = str(sys.argv[2])

  make(source_dir, source_name, target_dir)

