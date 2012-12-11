import relax

def make(source_dir, source_name, target_dir, num_cores):
  relax.make(source_dir, source_name, target_dir, None, num_cores=num_cores)

