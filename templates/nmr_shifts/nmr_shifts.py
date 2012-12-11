import numpy
import sys, os, stat
import re

from castepy.cell import Cell
from castepy.calc import CastepCalc
from castepy.templates.nmr import nmr
from castepy.util import calc_from_path

def parse_species(s):
  s, i = re.findall(r'([A-Za-z]+)([0-9]+)', s)[0]
  return (s, int(i))

def make_submit_all_script(root_dir, runs):
  script_path = os.path.join(root_dir, "submit_all.sh")
  script = open(script_path, "w+")

  for target_dir, name in runs:
    print >>script, "cd %s" % target_dir
    print >>script, "qsub %s.sh" % name
    print >>script, "cd .."

  os.chmod(script_path, 0755)

def make_magres_accum_script(root_dir, root_name, runs):
  script_path = os.path.join(root_dir, "magres_accum.sh")
  script = open(script_path, "w+")

  for target_dir, name in runs:
    print >>script, "grep isc %s/%s.magres >> %s-isc.magres" % (target_dir, name, root_name)

  os.chmod(script_path, 0755) 

epsilon = 1.0e-1

if __name__ == "__main__":
  source_dir, name = calc_from_path(sys.argv[1])
  target_dir_prefix = sys.argv[2]

  if not os.path.isdir(target_dir_prefix):
    os.mkdir(target_dir_prefix)

  calc = CastepCalc(source_dir, name)
  calc.load(include=["cell"])

  runs = []
  for ion in calc.cell.ions:
    p_orig = numpy.array(ion.p)

    for x, y, z in [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]:
      print x, y, z

      ion.p = p_orig + epsilon * numpy.array([x,y,z])
      run_dir = "%s-%s-%d-%d-%d-%d" % (name, ion.s, ion.i, x, y, z)

      target_dir = os.path.join(target_dir_prefix, run_dir)

      if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

      nmr.make(source_dir, name, target_dir, name, Cell(str(calc.cell)))
      runs.append((run_dir, name))

  make_submit_all_script(target_dir_prefix, runs)
  make_magres_accum_script(target_dir_prefix, name, runs)

