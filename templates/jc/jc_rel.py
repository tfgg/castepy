import jc

def make(source_dir, source_name, target_dir, target_name=None, jc_s=None, jc_i=None):
  return jc.make(source_dir, source_name, target_dir, target_name, jc_s, jc_i, True)
