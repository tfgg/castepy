import sys
import re

# Final energy, E             =  -126966.5122468     eV

energy_regex = re.compile("Final energy, E\s+=\s{0,}([0-9.\-]+)\s+eV")

class CantFindEnergy(Exception):
  pass

def parse(castep_file):
  energies = energy_regex.findall(castep_file)
  
  if len(energies) == 0:
    raise CantFindEnergy()
  else:
    return float(energies[len(energies)-1])

if __name__ == "__main__":
  print parse(open(sys.argv[1]).read())
