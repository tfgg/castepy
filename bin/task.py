#!/home/green/bin/python

import os, sys
from castepy.cell import Cell
from castepy.util import calc_from_path
import castepy.settings as settings

def path(s):
  return os.path.join(settings.CASTEPY_ROOT, s)

tasks = {'jc': path('templates/jc/jc.py'),
         'relax-H': path('templates/relax/relax.py'),
         'relax-full': path('templates/relax/relax-full.py'),
         'copy': path('templates/copy/copy.py'),
         'nmr': path('templates/nmr/nmr.py'),}

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "Available tasks:", ", ".join(tasks)
    sys.exit()

  task = str(sys.argv[1])
  source_path = str(sys.argv[2])
  source_dir, source_name = calc_from_path(source_path)
  target_dir = str(sys.argv[3])

  module_path = tasks[task]
  module_dir, module_file = os.path.split(module_path)
  module_name, _ = os.path.splitext(module_file)

  sys.path.append(module_dir)
  
  m = __import__(module_name)

  m.make(source_dir, source_name, target_dir)

