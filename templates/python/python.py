import sys, os
import shutil

import castepy.settings as settings

py_path = os.path.join(settings.CASTEPY_ROOT, "templates/python")

def make(source_dir, source_name, target_dir, target_name=None):
  if target_name is None:
    target_name = source_name

  sh_target = os.path.join(target_dir, "%s.sh" % target_name)

  sh_context = {'scriptname': target_name,
                'num_nodes': 32,
                'CASTEPY_ROOT': settings.CASTEPY_ROOT,}

  sh_source = open(os.path.join(py_path, "python.sh")).read()
  sh_target_file = open(sh_target, "w+")
  print >>sh_target_file, sh_source % sh_context
  sh_target_file.close()

if __name__ == "__main__":
  pass

