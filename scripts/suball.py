#!python

import sys, os
import pipes

def find_all_ext(path, ext, found):
  for file in os.listdir(path):
    file_path = os.path.join(path, file)
    if os.path.isdir(file_path):
      find_all_ext(file_path, ext, found)
    else:
      if ext == file.split('.')[-1]:
        found.append(file_path)

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    search_paths = sys.argv[1:]
  else:
    search_paths = [os.getcwd()]

  found_all = []
  for search_path in search_paths:
    found = []
    find_all_ext(search_path, "sh", found)

    found_all = found_all + [f for f in found if "submit_all.sh" not in f]

  root_path = os.getcwd()

  script_path = 'submit_all.sh'
  f_sh = open(script_path, 'w+')

  for script in found_all:
    dir, file = os.path.split(script)

    print >>f_sh, "cd %s" % pipes.quote(dir)
    print >>f_sh, "qsub %s" % pipes.quote(file)
    print >>f_sh, "cd %s" % pipes.quote(root_path)

  os.chmod(script_path, 0755)
