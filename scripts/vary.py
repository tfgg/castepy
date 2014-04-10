#!python
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
  extra = []
  vars = []

  current_var = None

  for arg in args:
    if arg.startswith('--'):
      current_var = arg[2:]
    else:
      if current_var is not None:
        vars.append((current_var, arg))
        current_var = None
      else:
        extra.append(arg)

  return (extra, vars) 

extra, vars = parse_args(sys.argv[1:])

target_dir = extra[0]
sources = extra[1:]

vars_values = []

def any(xs):
  for x in xs:
    if x:
      return True
  else:
    return False

for var_name, values in vars:
  values = values.split(",")

  try:
    if any(['.' in value for value in values]):
      values = map(float, values)
    else:
      values = map(int, values)

  except ValueError:
    pass

  vars_values.append((var_name, values))

vars_values_dict = dict(vars_values)
num_calcs = 0

# Take inner product of all our arguments and produce a dictionary of values
for vars_value in list(itertools.product(*[values for var_name, values in vars_values])):
  template_context = dict(zip([var_name for var_name, _ in vars_values], vars_value))

  # Generate name from varying arguments
  name = []
  for var_name, _ in vars_values:
    if len(vars_values_dict[var_name]) > 1:
      value = template_context[var_name]

      if type(value) == str:
        value = value.replace(' ', '_')

      name.append("{0}={1}".format(var_name, value))

  dir_path = os.path.join(target_dir, *name)

  # Make dir if it doesn't already exist
  for i in range(1,len(name)+1):
    check_dir_path = os.path.join(target_dir, *name[:i])

    if not os.path.isdir(check_dir_path):
      os.mkdir(check_dir_path)

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

