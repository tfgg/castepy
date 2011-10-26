#!/home/green/bin/python

import sys, os, stat
import re

from castepy.util import calc_from_path

import task

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
    print >>script, "grep efg %s/%s.magres >> %s-isc.magres" % (target_dir, name, root_name)

  os.chmod(script_path, 0755) 

if __name__ == "__main__":
  task_name = sys.argv[1]
  source_dir = sys.argv[2]
  target_dir_prefix = sys.argv[3]

  if not os.path.isdir(target_dir_prefix):
    os.mkdir(target_dir_prefix)

  runs = []
  for cell_path in [x for x in os.listdir(source_dir) if ".cell" in x]:
    dir, name = calc_from_path(cell_path)
    run_dir = name
    target_dir = os.path.join(target_dir_prefix, run_dir)

    if not os.path.isdir(target_dir):
      os.mkdir(target_dir)
    
    task.make_task(task_name, source_dir, name, target_dir)

    runs.append((run_dir, name))

  make_submit_all_script(target_dir_prefix, runs)
  #make_magres_accum_script(target_dir_prefix, name, runs)

