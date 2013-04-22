import jc

def make(*args, **kwargs):
  kwargs['rel_pot'] = True
  return jc.make(*args, **kwargs)
