import os, sys
import re

# |  dE/ion   |   4.399379E-004 |   5.000000E-006 |         eV | No  | <-- BFGS

step_parts = re.compile("^ \|\s+(.*?)\s+\|\s+([0-9A-Z\.\-\+]+)\s+\|\s+([0-9A-Z\.\-\+]+)\s+\|\s+(.*?)\s+\|\s+(.*?)\s+\| <-- BFGS", re.M)

def read_castep_file(castep_file):
  bfgs_step_parts = step_parts.findall(castep_file)

  curr = []
  steps = [curr]
  for step_part in bfgs_step_parts:
    if len(curr) == 3:
      curr = []
      steps.append(curr)
    step = {'param': step_part[0],
             'value': float(step_part[1]),
             'tol': float(step_part[2]),
             'unit': step_part[3],
             'ok': step_part[4],}
    curr.append(step)

  return steps

if __name__ == "__main__":
  steps = read_castep_file(open(sys.argv[1]).read())

  print "#N", " ".join([str(s['param']) for s in steps[0]])
  for i, step in enumerate(steps):
    print i, " ".join([str(s['value']) for s in step])
