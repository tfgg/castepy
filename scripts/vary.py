"""

  Script for varying a bunch of variables in a bunch of files to generate a bunch of calculations.

  Makes a directory for each, labelled by varied variables, i.e. ones with more than one value.

  vary.py --var1 A,B,C,D --var2 10,20,30,40 --var3 "arse" [target root dir] [files]

  Specify variables in files using new-style python format notation:

  mpirun -np {ncpu:%f} {code:%s} {seed:%s}

"""

import sys
import argparse
import itertools
import os, os.path

def parse_args(args):
  variables = {None: []}

  current_var = None

  for arg in args:
    if arg.startswith('--'):
      var_name = arg[2:]
      current_var = var_name
    else:
      if current_var is not None:
        variables[current_var] = arg
        current_var = None
      else:
        variables[current_var].append(arg)

  return variables

vars = parse_args(sys.argv[1:])

target_dir = vars[None][0]
sources = vars[None][1:]

vars_values = {}

def any(xs):
  for x in xs:
    if x:
      return True
  else:
    return False

for var_name in vars:
  if var_name is not None:
    values = vars[var_name].split(",")
  
    try:

      if any(['.' in value for value in values]):
        values = map(float, values)
      else:
        values = map(int, values)

    except ValueError:
      pass

    vars_values[var_name] = values

  else:
    pass

num_calcs = 0

# Take inner product of all our arguments and produce a dictionary of values
for vars_value in list(itertools.product(*[values for _, values in vars_values.items()])):
  template_context = dict(zip(vars_values.keys(), vars_value))

  # Generate name from varying arguments
  name = []
  for var_name in vars_values:
    if len(vars_values[var_name]) > 1:
      name.append("{0}={1}".format(var_name, template_context[var_name]))

  dir_name = ",".join(name)
  dir_path = os.path.join(target_dir, dir_name)

  # Make dir if it doesn't already exist
  if not os.path.isdir(dir_path):
    os.mkdir(dir_path)

  # Generate our source files from template and write out
  for source in sources:
    source_content = open(source, "r").read()
    _, source_name = os.path.split(source)

    source_target = os.path.join(dir_path, source_name)

    #print source_target
    #print source_content
    #print template_context
    print >>open(source_target, "w+"), source_content.format(**template_context), 

  num_calcs += 1

print "{0} calculations written to {1}".format(num_calcs, target_dir)

