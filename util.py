import os

def calc_from_path(path):
  """
    Given a file from a calculation (e.g. foo/bar.cell), infer the calculation directory and name (foo, bar)
  """

  dir, f = os.path.split(path)
  name, ext = os.path.splitext(f)

  return (dir, name)

def find_all_calcs(dir):
  calcs = []
  for f in os.listdir(dir):
    path = os.path.join(dir, f)
    if ".cell" in f:
      calcs.append(path)
    elif os.path.isdir(path):
      calcs += find_all_calcs(path)
  
  return calcs
