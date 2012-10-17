# -*- coding: utf-8 -*-
import os
import os.path
import numpy
from ion import Ion, Ions

class Parameters:
  def __init__(self, params=None):
    self.__dict__['params'] = {}

    if params is not None:
      if type(params) is dict:
        self.params = params
      elif type(params) is str:
        self.params = self.parse_params(params)
      elif type(params) is file:
        self.params = self.parse_params(params.read())

    print self.params

  def parse_params(self, params):
        import re
        split_re = re.compile("\s{0,}[=:]\s{0,}")
        comments_re = re.compile("![^\n]+")

        plines = params.split("\n")

        params = {}
        for pline in plines:
            pline = comments_re.sub("", pline)
            nv = split_re.split(pline)
            
            if len(nv) == 2:
                params[nv[0].strip()] = nv[1].strip()
        
        return params

  def __setitem__(self, n, v):
    self.params[n] = v
  
  def __setattr__(self, n, v):
    if n in self.__dict__:
      self.__dict__[n] = v 
    else:
      self.params[n] = v
    
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
    return "\n".join(["%s: %s" % (n ,v) for n, v in self.params.items()])

class Calculation:
    def __init__(self, cell=None, param=None, cell_file_path=None, param_file_path=None, required_files=[]):
        self.cell = cell
        self.param = param
        
        self.dir_path = None
        self.cell_file_name = "seed.cell"
        self.param_file_name = "seed.param"

        # Files to link into execution directory
        self.required_files = set(required_files)

        # We're given a cell file to load from
        if cell_file_path is not None:
            self.cell_file_path = os.path.abspath(cell_file_path)
            _, self.cell_file_name = os.path.split(cell_file_path)
            
            # If we don't have a cell loaded, and we have a cell file, load cell from that cell file
            if self.cell is None:
                self.cell = Cell(open(self.cell_file_path).read())
            else:
                self.cell = ""
        else:
            self.cell_file_name = "seed.cell"

        # We're given a param file to load from
        if param_file_path is not None:
            self.param_file_path = os.path.abspath(param_file_path)
            _, self.param_file_name = os.path.split(param_file_path)
            
            # If we don't have a param loaded, and we have a param file, load param from that param file
            if self.param is None:
                self.param = Parameters(open(self.param_file_path))
            else:
                self.param = ""
        else:
            self.param_file_name = "seed.param"

        self.seed_name = self.param_file_name.split(".")[0]
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        """ This ensures it's cleaned up, even if there's an exception """
        # self.clean()
        return False

    def make_dir(self, prefix="tmp"):
        """
            Make a temporary directory for Castep to do calculations in
        """
        import tempfile

        if self.dir_path is None:
            self.dir_path = tempfile.mkdtemp(dir="./tmp", prefix=prefix)

    def link_required_files(self, dir_path):
        for f in self.required_files:
            f = os.path.abspath(f)            
            d, filename = os.path.split(f)
            target = os.path.join(dir_path, filename)
            os.symlink(f, target)
            
            # print os.getcwd(), f, target

    def write_seed(self):
        """
            Write the seed files seed.cell and seed.param based on provided
            input structures (which could be objects or strings)
        """
        self.cell_file = open(os.path.join(self.dir_path, self.cell_file_name), "w+")
        self.param_file = open(os.path.join(self.dir_path, self.param_file_name), "w+")

        self.cell_file.write("%s" % self.cell)
        self.param_file.write("%s" % self.param)

        self.cell_file.flush()
        os.fsync(self.cell_file)
        self.param_file.flush()
        os.fsync(self.param_file)

        self.link_required_files(self.dir_path)

    def write(self, prefix="tmp", dir_path=None):
        """
            Prepare the temporary directory and seed files
        """
        if dir_path is None:
          self.make_dir(prefix)
        else:
          self.dir_path = dir_path
          if not os.path.isdir(dir_path):
              os.mkdir(dir_path)
          
        self.write_seed()
    
    def clean(self):
        """
            Clean up our directory
        """
        import shutil
        
        self.cell_file.close()
        self.param_file.close()
        shutil.rmtree(self.dir_path)

class SimpleCalculation:
    def __init__(self, dir_path, seed_name="seed"):
        self.dir_path = dir_path
        self.seed_name = seed_name

    def has_run(self):
        if os.path.exists(os.path.join(self.dir_path, self.seed_name + ".castep")):
	    return True
        else:
            return False

class Castep:
    castep_path = "/users2/green/CASTEP-5.5/obj/linux_x86_64_ifort11/castep"
    sge_command = "qsub"
    sge_script = "/home/green/test_runs/run_mpi.sh"

    def __init__(self, castep_path=""):
        self.castep_path = castep_path
    
    def execute(self, calculation):
        """
            Execute Castep in our temporary directory via the shell
        """
        import subprocess

        retcode = subprocess.call([self.castep_path, calculation.seed_name], cwd=calculation.dir_path)

    def sge_execute(self, calculation, num_nodes=1):
        import subprocess

        retcode = subprocess.call([self.sge_command, self.sge_script, calculation.seed_name], cwd=calculation.dir_path)

