import os
import math
import re

import castepy.settings as settings
from castepy.input import pot, parameters
from castepy.input.cell import Cell
from castepy.input.parameters import Parameters
from castepy.utils import calc_from_path
from castepy.templates.submission_scripts import SubmissionScript

jc_path = os.path.join(settings.CASTEPY_ROOT, "templates/jc")

regex_species = re.compile('([A-Za-z]+)([0-9]+)')

class SiteNotPresent(Exception):
  pass

def round_cores_up(n, m):
  return int(math.ceil(float(n)/m)*m)

class JcouplingTask(object):
  merge_cell = Cell(open(os.path.join(jc_path, "jc.cell")).read())
  params = Parameters(open(os.path.join(jc_path, "jc.param")).read())
  code = "castep-jcusp.mpi"

  def __init__(self, num_cores=32, rel_pot=False, usp_pot=False, xc_functional='pbe', cut_off_energy=80, queue="parallel.q", jc_s, jc_i, cell=None, target_name=None, source=None):
    self.num_cores = num_cores
    self.rel_pot = rel_pot
    self.xc_functional = xc_functional.lower()
    self.cut_off_energy = cut_off_energy
    self.usp_pot = usp_pot
    self.queue = queue
    self.jc_s = jc_s
    self.jc_i = jc_i
    self.cell = cell
    self.target_name = target_name
    self.source = source

  def get_jcoupling_site(self, target_dir):
    """
      Prompt the user to enter a J-coupling site
    """

    species_matches = regex_species.findall(target_dir) 

    if species_matches:
      self.jc_s = species_matches[0][0]
      self.jc_i = int(species_matches[0][1])
      jsiteraw = raw_input("Specify the j-coupling site ({:s} {:d}): ".format(jc_s, jc_i))

      if jsiteraw:
        j_site = jsiteraw.split()
        self.jc_s = j_site[0]
        self.jc_i = int(j_site[1])
    else:
      jsiteraw = raw_input("Specify the j-coupling site: ")

      j_site = jsiteraw.split()
      self.jc_s = j_site[0]
      self.jc_i = int(j_site[1])
  
    return (self.jc_s, self.jc_i)

  def get_cell(self):
    """
      Make sure that self.cell is loaded, possibly by loading from source cell file.
    """

    if self.cell is None and self.source is None:
      raise Exception("One of cell or source must be provided")
    
    if self.source is None and self.target_name is None:
      raise Exception("If no cell is provided, target_name must be specified")

    if self.source is not None:
      source_dir, source_name = calc_from_path(self.source)

      if self.cell is None:
        self.cell = Cell(os.path.join(source_dir, "{}.cell".format(source_name)))

  def make(self, target_dir):
    """
      Write the calculation to the specified target directory.
    """

    self.get_cell()

    # Get the J-coupling site if we don't have it already
    if self.jc_s is None:
      self.get_jcoupling_site(target_dir) 

    # Set up the site in the cell
    if self.jc_s is not None:
      try:
        jc_ion = cell.ions.species(self.jc_s)[self.jc_i-1]
      except IndexError:
        raise SiteNotPresent("Site {:s} {:d} not present".format(self.jc_s, self.jc_i))
    
      cell.otherdict['jcoupling_site'] = "{:s} {:d}".format(self.jc_s, self.jc_i)

    # Remove extraneous kpoints and add in default cell setup
    if 'KPOINTS_LIST' in cell.blocks:
      del cell.blocks['KPOINTS_LIST']
    
    self.cell.otherdict.update(self.merge_cell.otherdict)
    
    # Sort out .param file
    self.params.xc_functional = self.xc_functional
    self.params.cut_off_energy = self.cut_off_energy

    # Add pseudopotentials
    if self.usp_pot:
      pot.add_potentials_usp(cell, self.rel_pot)
    else:
      potentials = pot.add_potentials_asc(cell, self.xc_functional, self.rel_pot)

      for potential in potentials:
        potential.link_files(target_dir)
    
    # Generate submission script and write all the files out
    if target_name is None:
      target_name = source_name

    cell_target = os.path.join(target_dir, "%s.cell" % target_name)
    param_target = os.path.join(target_dir, "%s.param" % target_name)
    sh_target = os.path.join(target_dir, "%s.sh" % target_name)

    submission_script = SubmissionScript(self.queue,
                                         self.num_cores,
                                         self.code,
                                         target_name)


    with open(sh_target, "w+") as sh_target_file,
         open(param_target, "w+") as param_target_file,
         open(cell_target, "w+") as cell_target_file:

      print >>sh_target_file, submission_script
      print >>param_target_file, self.params
      print >>cell_target_file, self.cell

