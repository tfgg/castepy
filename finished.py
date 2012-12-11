#!/home/green/bin/python
import os, sys
import re

from util import calc_from_path

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

if __name__ == "__main__":
  cwd, name = calc_from_path(sys.argv[1])

  print "Checking %s in %s" % (name, cwd)

  errors = error_check(cwd, name)
  if errors is not None:
    print "Errors found:"
    print errors
  else:
    print "No errors found"

  if not castep_finished(cwd, name):
    print "Castep not finished"
  else:
    print "Castep finished"
