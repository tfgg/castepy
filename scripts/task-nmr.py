#!python
import sys, os
import argparse

from castepy.utils import calc_from_path
from castepy.tasks import NMRTask

parser = argparse.ArgumentParser(description='Create a CASTEP NMR calculation.')

parser.add_argument('target_dir', help='A directory to build the calculation in.')
parser.add_argument('source', nargs=argparse.REMAINDER, help='Cell file(s) to build the calculation from.')
parser.add_argument('-n', '--num_cores', type=int, help='Number of cores to use.', default=32)
parser.add_argument('-q', '--queue', type=str, help='SGE queue to use.', default="parallel.q")
parser.add_argument('-x', '--xc_functional', help='The XC functional to use', default="PBE")
parser.add_argument('-c', '--cut_off_energy', type=int, help='The cut-off energy to use (Rydberg)', default=50)
parser.add_argument('-e', '--efg_only', action="store_const", const=True, default=False, help="Only do an EFG calculation")
parser.add_argument('-p', '--pot', help='What type(s) of pseudopotentials to use, separated by commas.', type=str, default="usp")
parser.add_argument('-r', '--pot_type', type=str, default=None, help="Pseudopotential type (for USPs), e.g. kh, schro, zora, dirac")

def make_command(args):
  a = parser.parse_args(args)

  if a.pot == "usp":
    usp_pot = True
  else:
    usp_pot = False

  for source in a.source:
    task = NMRTask(source=source,
                   num_cores=a.num_cores,
                   queue=a.queue,
                   xc_functional=a.xc_functional,
                   cut_off_energy=a.cut_off_energy,
                   usp_pot=usp_pot,
                   pot_type=a.pot_type,
                   efg_only=a.efg_only)
       
    source_dir, source_name = calc_from_path(source)
    target_dir = os.path.join(a.target_dir, source_name)

    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    task.make(target_dir)

if __name__ == "__main__":
  make_command(sys.argv[1:])

