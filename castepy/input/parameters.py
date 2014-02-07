import re
import os.path

from valid_params import valid_params

def makeparam(ss):
  try:
    ss = ss.strip().split()
  except AttributeError:
    return [ss]
  else:
    def try_cast(s):
      try:
        return int(s)
      except:
        try:
          return float(s)
        except:
          return str(s)

    ss_conv = map(try_cast, ss)

    return ss_conv

class UnrecognisedParameter(Exception):
  pass

class Parameters:
  def __init__(self, params=None):
    self.__dict__['params'] = {}
    self.__dict__['comments'] = []

    if params is not None:
      if type(params) is dict:
        self.params = params
      elif type(params) is str:
        if os.path.isfile(params):
          self.params, self.comments = self.parse_params(open(params).read())
        else:
          self.params, self.comments = self.parse_params(params)
      elif type(params) is file:
        self.params, self.comments = self.parse_params(params.read())

  def parse_params(self, params):
    import re
    split_re = re.compile("\s{0,}[=:]\s{0,}")
    comments_re = re.compile("![^\n]+")

    plines = params.split("\n")

    comments = []
    params = {}
    for pline in plines:
        pline = pline.strip()

        if comments_re.match(pline):
           comments.append(pline)
        else:
          pline = comments_re.sub("", pline)
          nv = split_re.split(pline)
          
          if len(nv) == 2:
            name = nv[0].strip()
            value = nv[1].strip()

            params[name] = makeparam(nv[1])
    
    return params, comments

  def __setitem__(self, n, v):
    self.params[n] = v
  
  def __setattr__(self, n, v):
    if n in self.__dict__:
      self.__dict__[n] = v 
    else:
      if n not in valid_params:
        raise UnrecognisedParameter(n)
      else:
        if n in self.params and type(v) in [int, float]:
          self.params[n][0] = v
        else:
          self.params[n] = makeparam(v)
    
  def __getitem__(self, n):
    if n in self.params:
      return self.params[n]
    else:
      raise KeyError

  def __getattr__(self, key):
    if key in self.params:
      return self.params[key]
    else:
      raise AttributeError(key)

  def __str__(self):
    lines = []
    lines += ["%s: %s" % (n , " ".join(map(str,v))) for n, v in self.params.items()]
    lines += self.comments
    return "\n".join(lines)
