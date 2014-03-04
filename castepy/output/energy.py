import sys
import re
import math

# Final energy, E             =  -126966.5122468     eV

class TotalEnergyResult(object):
  class CantFindEnergy(Exception):
    pass

  energy_regex = re.compile("Final energy, E\s+=\s{0,}([0-9.\-]+)\s+eV")
  energy_regex2 = re.compile("Final energy\s+=\s{0,}([0-9.\-]+)\s+eV")

  @classmethod
  def load(klass, castep_file):
    energies = klass.energy_regex.findall(castep_file)
    energies += klass.energy_regex2.findall(castep_file)

    if len(energies) == 0:
      raise klass.CantFindEnergy()
    else:
      for energy in energies:
        yield float(energy), 'eV'

class SCFResult(object):
  find_lines = re.compile(r'(.*?)\<\-\- SCF\n')

  def __init__(self, scf_run):
    self.steps = scf_run

  def __str__(self):
    lines = ["# loop energy energy_gain log_energy_gain timer"]
    
    for step in self.steps:
      lines.append("{loop} {energy} {energy_gain} {log_gain} {time}".format(**step))

    return "\n".join(lines)

  @classmethod
  def load(klass, castep_file):
    scf_lines = klass.find_lines.findall(castep_file)

    scf_run = []

    for line in scf_lines:
      cols = line.split()

      if len(cols) == 1 or len(cols) == 6 or len(cols) == 7:
        continue
      elif len(cols) == 3:
        if cols[0] == 'Initial':
          loop = 0
          energy, timer = cols[1:]
          energy_gain = 1.0
        elif cols[0] in ['per', 'Real']:
          continue
      elif len(cols) == 4:
        loop, energy, energy_gain, timer = cols
      elif len(cols) == 5:
        loop, energy, fermi_energy, energy_gain, timer = cols
      else:
        continue
        
      if loop == 'energy':
        continue

      if loop == 'Initial':
        loop = 0
        energy_gain = 1.0

      loop = int(loop)
      energy = float(energy)
      energy_gain = float(energy_gain)
      timer = float(timer)
        
      if scf_run and loop == 0:
        yield SCFResult(scf_run)
        scf_run = []

      scf_run.append({'loop': loop,
                      'energy': energy,
                      'energy_gain': energy_gain,
                      'log_gain': math.log(abs(energy_gain), 10),
                      'time': timer})

    yield SCFResult(scf_run)

