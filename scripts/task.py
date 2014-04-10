#!python

import os, sys, getopt
from castepy.input.cell import Cell
from castepy.utils import calc_from_path, path

import castepy.settings as settings

tasks = {'jc': path('templates/jc/jc.py'),
         'jc-full': path('templates/jc_full/jc_full.py'),
         'relax-H': path('templates/relax/relax.py'),
         'relax-full': path('templates/relax/relax-full.py'),
         'copy': path('templates/copy/copy.py'),
         'nmr': path('templates/nmr/nmr.py'),
         'energy': path('templates/energy/energy.py'),
         'psptest': path('templates/psptest/psptest.py'),
         'spectral': path('templates/spectral/spectral.py'),
         'python': path('templates/python/python.py'),}


def make_task(task, args):
  module_path = tasks[task]
  module_dir, module_file = os.path.split(module_path)
  module_name, _ = os.path.splitext(module_file)

  sys.path.append(module_dir)
  
  m = __import__(module_name)

  #source_dir, source_name, target_dir, 

  m.make_command(args)

def inquire_num_cores():
  num_cores = 32
  num_cores_raw = raw_input("How many cores? (%d): " % (num_cores))
  
  try:
    num_cores = int(num_cores_raw)
  except:
    pass

  return num_cores

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "Available tasks:", ", ".join(tasks)
    sys.exit()

  task = str(sys.argv[1])

  make_task(task, sys.argv[2:])

