import math

class Accum:
  """
    Accumulator to make statistics
  """

  def __init__(self, bins):
    self.bins = bins
    self.count = dict([(x, 0) for x in bins])
    self.sum = dict([(x, 0.0) for x in bins])
    self.sumsq = dict([(x, 0.0) for x in bins])

  def add(self, x, y, w=1.0):
    self.count[x] += w
    self.sum[x] += y*w
    self.sumsq[x] += (y*w)**2

  def mean(self):
    return dict([(x,self.sum[x] / self.count[x]) for x in self.bins if self.count[x] != 0])
  
  def sd(self):
    mean = self.mean()
    return dict([(x, math.sqrt(self.sumsq[x] / self.count[x] - mean[x]**2)) for x in self.bins if self.count[x] != 0])

  def __str__(self):
    means = self.mean()
    sd = self.sd()

    return "\n".join(["%s %f %f %f" % (str(bin), self.count[bin], means[bin], sd[bin]) for bin in self.bins])

  def as_csv(self):
    means = self.mean()
    sd = self.sd()

    return "\n".join(["%s %f %f %f" % (" ".join(map(str,bin)), self.count[bin], means[bin], sd[bin]) for bin in self.bins])

