#!/home/green/bin/python

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
  found = []

  if len(sys.argv) >= 2:
    search_path = sys.argv[1]
  else:
    search_path = os.getcwd()

  find_all_ext(search_path, "sh", found)

  found = [f for f in found if "submit_all.sh" not in f]

  root_path = os.getcwd()

  script_path = 'submit_all.sh'
  f_sh = open(script_path, 'w+')

  for script in found:
    dir, file = os.path.split(script)

    print >>f_sh, "cd %s" % pipes.quote(dir)
    print >>f_sh, "qsub %s" % pipes.quote(file)
    print >>f_sh, "cd %s" % pipes.quote(root_path)

  os.chmod(script_path, 0755)
