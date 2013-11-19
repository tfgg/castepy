import relax

def make(source, target_dir, num_cores, **kwargs):
  relax.make(source, target_dir, None, num_cores=num_cores, **kwargs)

