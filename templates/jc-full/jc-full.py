import sys, os, stat
import re

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
  species = map(parse_species, sys.argv[3:])

  if not os.path.isdir(target_dir_prefix):
    os.mkdir(target_dir_prefix)

  runs = []
  for s, i in species:
    run_dir = "%s-%s%d" % (name, s, i)
    target_dir = os.path.join(target_dir_prefix, run_dir)

    if not os.path.isdir(target_dir):
      os.mkdir(target_dir)
     
    jc.make(source_dir, name, target_dir, name, s, i)
    runs.append((run_dir, name))

  make_submit_all_script(target_dir_prefix, runs)
  make_magres_accum_script(target_dir_prefix, name, runs)

