#!python
import shutil
import re
import itertools

from castepy.utils import calc_from_path
from castepy.tasks import JcouplingTask

import argparse

parser = argparse.ArgumentParser(description='Create a CASTEP J-coupling calculation.')
parser.add_argument('target_dir', help='Directory to build the calculation(s) in.')
parser.add_argument('source', nargs=argparse.REMAINDER, help='Cell file(s) to build the calculation from.')
parser.add_argument('-n', '--num_cores', type=int, help='Number of cores to use.', default=8)
parser.add_argument('-q', '--queue', type=str, help='SGE queue to use.', default="parallel.q")
parser.add_argument('-s', '--site', help='Target J-coupling site(s), separated by commas. Warning if site not present in structure.', type=str)
parser.add_argument('-r', '--rel', action="store_const", help='Use relativity', default=False, const=True)
parser.add_argument('-p', '--pot', help='What type(s) of pseudopotentials to use, separated by commas.', type=str, default="ncp")
parser.add_argument('-x', '--xc_functional', help='The XC functional(s) to use, separated by commas.', default="PBE")
parser.add_argument('-c', '--cut_off_energy', type=str, help='The cut-off energy(s) to use (Rydberg), separated by commas.', default="80")

regex_species = re.compile('([A-Za-z]+)([0-9]+)')

def make_command(args):
  a = parser.parse_args(args)

  print a.__dict__

  sites = []
  if a.site is not None:
    for site in a.site.split(","):
      sites.append(regex_species.findall(site)[0])
  else:
    sites = [None]

  cut_off_energies = map(int,a.cut_off_energy.split(","))
  xc_functionals = [s.lower() for s in a.xc_functional.split(",")]
  pots = a.pot.split(",")
  sources = a.source

  param_prod = list(itertools.product(sources, sites, cut_off_energies, xc_functionals, pots))

  for source,site,cut_off_energy,xc_functional,pot in param_prod:

    source_dir, source_name = calc_from_path(source)

    # Set up following directory structure:
    # [rel/nrel]/[usp/ncp]/[xc_functional]/[structure]/[cutoff]/[site]

    dir_path = [a.target_dir]

    if len(pots) > 1:
      dir_path.append(pot)
    
    if len(xc_functionals) > 1:
      dir_path.append(xc_functional)

    if len(sources) > 1:
      dir_path.append(source_name)

    if len(cut_off_energies) > 1:
      dir_path.append("%dry" % cut_off_energy)

    if len(sites) > 1:
      dir_path.append("".join(site))

    print dir_path

    new_dir = False

    for i in range(len(dir_path)):
      d = os.path.join(*dir_path[:i+1])

      if not os.path.isdir(d):
        os.mkdir(d)
        new_dir = True

    target_dir = os.path.join(*dir_path)

    if site is not None:
      jc_s, jc_i = site
      jc_i = int(jc_i)
    else:
      jc_s = None
      jc_i = None

    if pot == "usp":
      usp_pot = True
    elif pot == "ncp":
      usp_pot = False

    try:
      task = JcouplingTask(num_cores=a.num_cores,
                           rel_pot=a.rel,
                           usp_pot=usp_pot,
                           xc_functional=xc_functional,
                           cut_off_energy=cut_off_energy,
                           queue=a.queue,
                           jc_s=jc_s,
                           jc_i=jc_i,
                           source=source)

      task.make(target_dir)

    except SiteNotPresent, e:
      print e

      # If we've just made this directory, trash it
      if new_dir:
        shutil.rmtree(target_dir)

if __name__ == "__main__":
  make_command(sys.argv[1:])
