import os

import castepy.settings as settings
from castepy.input import pot
from castepy.input.cell import Cell
from castepy.input.parameters import Parameters
from castepy.templates.submission_scripts import SubmissionScript
from castepy.util import calc_from_path

nmr_path = os.path.join(settings.CASTEPY_ROOT, "templates/nmr")

class NMRTask(object):
  merge_cell = Cell(open(os.path.join(nmr_path, "nmr.cell")).read())
  params = Parameters(open(os.path.join(nmr_path, "nmr.param")).read())
  code = "castep-jcusp.mpi"

  def __init__(self, cell=None, source=None, target_name=None, num_cores=32, queue="parallel.q", xc_functional="pbe", cut_off_energy=50, usp_pot=True, rel_pot=True, efg_only=False):
    self.cell = cell
    self.source = source
    self.target_name = target_name
    self.num_cores = num_cores
    self.queue = queue
    self.xc_functional = xc_functional.lower()
    self.cut_off_energy = cut_off_energy
    self.usp_pot = usp_pot
    self.rel_pot = rel_pot
    self.efg_only = efg_only

  def get_cell(self):
    """
      Make sure that self.cell is loaded, possibly by loading from source cell file.
    """

    if self.cell is None and self.source is None:
      raise Exception("One of cell or source must be provided")
    
    if self.source is None and self.target_name is None:
      raise Exception("If no cell is provided, target_name must be specified")

    if self.source is not None:
      source_dir, self.source_name = calc_from_path(self.source)

      if self.cell is None:
        self.cell = Cell(os.path.join(source_dir, "{}.cell".format(self.source_name)))

  def make(self, target_dir):
    self.get_cell()

    self.cell.otherdict.update(self.merge_cell.otherdict)
    self.cell.blocks.update(self.merge_cell.blocks)

    if self.usp_pot:
      pot.add_potentials_usp(self.cell, self.rel_pot)

    else:
      potentials = pot.add_potentials_asc(self.cell, self.xc_functional, self.rel_pot)
      
      for potential in potentials:
        potential.link_files(target_dir)

    self.params.xc_functional = self.xc_functional
    self.params.cut_off_energy = self.cut_off_energy

    if self.efg_only:
      self.params.magres_task = "efg"
    else:
      self.params.magres_task = "nmr"

    if self.target_name is None:
      self.target_name = self.source_name

    cell_target = os.path.join(target_dir, "%s.cell" % self.target_name)
    param_target = os.path.join(target_dir, "%s.param" % self.target_name)
    sh_target = os.path.join(target_dir, "%s.sh" % self.target_name)

    submission_script = SubmissionScript(self.queue,
                                         self.num_cores,
                                         self.code,
                                         self.target_name)

    with open(sh_target, "w+") as sh_target_file,\
         open(param_target, "w+") as param_target_file,\
         open(cell_target, "w+") as cell_target_file:

      print >>sh_target_file, submission_script
      print >>param_target_file, self.params
      print >>cell_target_file, self.cell

