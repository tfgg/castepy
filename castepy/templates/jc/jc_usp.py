import jc

def make(*args, **kwargs):
  kwargs['usp_pot'] = True
  return jc.make(*args, **kwargs)
