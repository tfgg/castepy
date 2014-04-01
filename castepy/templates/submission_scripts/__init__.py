import os.path
import math
import pipes

import castepy.settings as settings


PATH, _ = os.path.split(os.path.realpath(__file__))

def getfile(p):
  return open(os.path.join(PATH, p)).read()

sub_map = {'ironman': getfile('ironman.sh'),
           'kittel': getfile('kittel.sh'),
           'hector': getfile('hector.pbs'),
           'archer': getfile('archer.pbs')}

def get_submission_script(platform):
  return sub_map[platform]

def round_cores_up(n, m):
  return int(math.ceil(float(n)/m)*m)

class SubmissionScript(object):
  platform = settings.PLATFORM

  def __init__(self, queue, num_cores, code, seedname, platform=None):
    if platform is not None:
      self.platform = platform
    
    self.queue = queue
    self.num_cores = num_cores
    self.code = code
    self.seedname = seedname

    self.calc()

  def calc(self):
    cores_per_node = None

    if self.platform == "ironman":
      if self.queue in ["parallel.q", "shortpara.q"]:
        cores_per_node = 8
      elif self.queue == "serial.q":
        cores_per_node = 1
      elif self.queue == "newpara.q":
        cores_per_node = 12

    elif self.platform == "kittel":
      if self.queue in ["parallel.q", "shortpara.q"]:
        cores_per_node = 8
      elif self.queue == "serial.q":
        cores_per_node = 1
    elif self.platform == "archer":
      cores_per_node = 24
    elif self.platform == "hector":
      cores_per_node = 32
    else:
      raise Exception("Don't know cores per node for platform '%s'" % self.platform)

    self.num_round_cores = round_cores_up(self.num_cores, cores_per_node)
    self.num_nodes = self.num_round_cores / cores_per_node

    self.h_vmem = None

    if self.platform == "ironman":
      if self.queue in ["parallel.q", "shortpara.q"]:
        self.h_vmem = 23.0 / 8 * self.num_round_cores
      elif self.queue == "serial.q":
        self.h_vmem = 23.0 / 8 * self.num_round_cores
      elif self.queue == "newpara.q":
        self.h_vmem = 63.0 / 12 * self.num_round_cores
    elif self.platform == "kittel":
      if self.queue in ["parallel.q", "shortpara.q"]:
        self.h_vmem = 23.0 / 8
      elif self.queue == "serial.q":
        self.h_vmem = 23.0 / 8

    elif self.platform == "archer":
      self.h_vmem = None

    else:
      raise Exception("Don't know memory requirements for platform '%s'" % self.platform)

    


  def data_dict(self):
    self.calc()
    return {'num_round_cores': self.num_round_cores,
            'num_nodes': self.num_nodes,
            'queue': self.queue,
            'h_vmem': self.h_vmem,
            'num_cores': self.num_cores,
            'code': self.code,
            'seedname': pipes.quote(self.seedname),}

  def __str__(self):
    return sub_map[self.platform] % self.data_dict()

