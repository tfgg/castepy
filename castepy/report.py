# Print out header information for every script to help reproduce results
import sys, os
from datetime import datetime

if __name__ != "__main__":
  print "#@script: %s" % os.path.join(os.getcwd(), sys.argv[0])
  print "#@args: %s" % ", ".join(sys.argv[1:])
  print "#@cwd: %s" % os.getcwd()
  print "#@date: %s" % datetime.now()
else:
  import re
  import subprocess

  input = open(sys.argv[2])

  header = re.findall("#@(.*?):(.*?)\n", input.read())

  input.close()

  deets = {}

  for name, value in header:
    deets[name] = value.strip()

    if name == "args":
      deets[name] = [arg.strip() for arg in deets[name].split(",")]


  if sys.argv[1] == "regen":
    output = open(sys.argv[1], "w+")
    print >>sys.stderr, "Regening %s" % deets
    rtn = subprocess.Popen(args=["python", deets["script"]] + deets["args"], cwd=deets["cwd"], stdout=output)
    print >>sys.stderr, rtn.wait()
    output.close()
  elif sys.argv[1] == "head":
    for name, value in deets.items():
      print "%s: %s" % (name, value)
 
