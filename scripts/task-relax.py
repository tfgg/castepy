#!python
import sys
import argparse

from castepy.tasks import GeometryRelaxationTask

parser = argparse.ArgumentParser(description='Create a CASTEP NMR calculation.')

parser.add_argument('target_dir', help='A directory to build the calculation in.')
parser.add_argument('source', help='A cell file to build the calculation from.')
parser.add_argument('-n', '--num_cores', type=int, help='Number of cores to use.', default=32)
parser.add_argument('-q', '--queue', type=str, help='SGE queue to use.', default="parallel.q")
parser.add_argument('-x', '--xc_functional', help='The XC functional to use', default="PBE")
parser.add_argument('-c', '--cut_off_energy', type=int, help='The cut-off energy to use (Rydberg)', default=50)
parser.add_argument('-p', '--pot', help='What type(s) of pseudopotentials to use, separated by commas.', type=str, default="usp")

def make_command(args):
  a = parser.parse_args(args)

  if a.pot == "usp":
    usp_pot = True
  else:
    usp_pot = False

  task = GeometryRelaxationTask(source=a.source,
                                num_cores=a.num_cores,
                                queue=a.queue,
                                xc_functional=a.xc_functional,
                                cut_off_energy=a.cut_off_energy,
                                usp_pot=usp_pot)
       
  task.make(a.target_dir)

if __name__ == "__main__":
  make_command(sys.argv[1:])

