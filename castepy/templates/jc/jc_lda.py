import jc

def make(*args, **kwargs):
  kwargs['xc'] = 'lda'

  return jc.make(*args, **kwargs)

