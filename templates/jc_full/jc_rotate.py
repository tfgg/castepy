import sys, os, stat
import re

from castepy.calc import CastepCalc
from castepy.templates.jc import jc
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

if __name__ == "__main__":
  source_dir, name = calc_from_path(sys.argv[1])
  target_dir_prefix = sys.argv[2]
  s = sys.argv[3]
  i = int(sys.argv[4])

  if not os.path.isdir(target_dir_prefix):
    os.mkdir(target_dir_prefix)

  runs = []
  for x in [float(xp)/100.0 for xp in range(0,60)]:
    run_dir = "%s-%f" % (name, x)
    target_dir = os.path.join(target_dir_prefix, run_dir)

    if not os.path.isdir(target_dir):
      os.mkdir(target_dir)

    calc = CastepCalc(source_dir, name)
    calc.load(include=["cell"])

    print calc.cell.lattice
    #calc.cell.ions.translate_origin((x*0.529177,x*0.529177,x*0.529177))
     
    #jc.make(source_dir, name, target_dir, name, s, i, True, calc.cell)
    #runs.append((run_dir, name))

  #make_submit_all_script(target_dir_prefix, runs)
  #make_magres_accum_script(target_dir_prefix, name, runs)

