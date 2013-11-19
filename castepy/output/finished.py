#!/home/green/bin/python
import os, sys
import re

from castepy.utils import calc_from_path

def error_check(cwd, name):
  files = os.listdir(cwd)

  errsize = 0
  for f in files:
    if name in f and ".err" in f:
      errsize += os.path.getsize(os.path.join(cwd, f))

  if errsize != 0:
    return True
  else:
    return None

def castep_finished(cwd, name):
  try:
    castep_file = open(os.path.join(cwd, "%s.castep" % name)).read()
    if len(re.findall("Writing analysis data to ", castep_file)) == 0:
      return False
    else:
      return True
  except IOError:
    return False

