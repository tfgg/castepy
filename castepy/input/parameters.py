import re

class IntWithUnits(int):
  def __new__(klass, value, units):
    obj = int.__new__(klass, value)
    obj.units = units
    return obj

  def __str__(self):
    return "%d %s" % (self, self.units)

class FloatWithUnits(float):
  def __new__(klass, value, units):
    obj = float.__new__(klass, value)
    obj.units = units 
    return obj
  
  def __str__(self):
    return "%f %s" % (self, self.units)

class StrWithUnits(str):
  def __new__(klass, value, units):
    obj = str.__new__(klass, value)
    obj.units = units
    return obj
  
  def __str__(self):
    return "%s %s" % (self, self.units)

def attempt_numeric(s):
  try:
    return int(s)
  except:
    try:
      return float(s)
    except:
      return s

def attempt_numeric_units(s, units):
  print s, units
  print type(s), type(units)

  try:
    return IntWithUnits(int(s), units)
  except ValueError:
    try:
      return FloatWithUnits(float(s), units)
    except ValueError:
      return StrWithUnits(s, units)

#def makeparam(s):
#  s = s.strip().split()
#
#  if len(s) == 1:
#    return attempt_numeric(s)
#  elif len(s) == 2:
#    return [attempt_numeric(s[0]), s[1]]
#  else:
#    raise Exception("Don't know how to handle multiple cols %s" % s)

def makeparam(ss):
  ss = ss.strip().split()

  def try_cast(s):
    try:
      return int(s)
    except:
      try:
        return float(s)
      except:
        return str(s)

  ss_conv = map(try_cast, ss)

  #if len(ss_conv) == 1:
  #  return ss_conv[0]
  #else:
  return ss_conv

class Parameters:
  def __init__(self, params=None):
    self.__dict__['params'] = {}
    self.__dict__['comments'] = []

    if params is not None:
      if type(params) is dict:
        self.params = params
      elif type(params) is str:
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
