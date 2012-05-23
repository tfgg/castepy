import sys
import re
import math

# Final energy, E             =  -126966.5122468     eV

energy_regex = re.compile("Final energy, E\s+=\s{0,}([0-9.\-]+)\s+eV")
energy_regex2 = re.compile("Final energy\s+=\s{0,}([0-9.\-]+)\s+eV")

class CantFindEnergy(Exception):
  pass

def parse(castep_file):
  energies = energy_regex.findall(castep_file)
  energies += energy_regex2.findall(castep_file)

  if len(energies) == 0:
    raise CantFindEnergy()
  else:
    return float(energies[len(energies)-1])

class SCFResult(object):
  find_lines = re.compile(r'(.*?)\<\-\- SCF\n')
  #loop_step = re.compile(r'\s{0,}(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s\s', re.S)

  def __init__(self, castep_file):
    self.load(castep_file)

  def load(self, castep_file):
    scf_lines = self.find_lines.findall(castep_file)

    self.scf_runs = []
    scf_run = []

    for line in scf_lines:
      cols = line.split()
      #print cols
      #cols = self.loop_step.findall(line)
      if len(cols) == 1 or len(cols) == 6 or len(cols) == 7:
        continue
      elif len(cols) == 3:
        if cols[0] == 'Initial':
          loop = 0
          energy, timer = cols[1:]
          energy_gain = 1.0
        elif cols[0] == 'per':
          continue
      elif len(cols) == 4:
        loop, energy, energy_gain, timer = cols
      elif len(cols) == 5:
        loop, energy, fermi_energy, energy_gain, timer = cols
      else:
        #print len(cols)
        continue
        
      #print loop, energy, energy_gain, timer

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
        self.scf_runs.append(scf_run)
        scf_run = []

      scf_run.append((loop, energy, energy_gain, math.log(abs(energy_gain), 10), timer))

    self.scf_runs.append(scf_run)

if __name__ == "__main__":
  scf_result = SCFResult(open(sys.argv[1]).read())
  print scf_result.scf_runs
  #print parse(open(sys.argv[1]).read())
