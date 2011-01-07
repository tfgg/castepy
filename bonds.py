import re
import sys
import castepy
import ion

def parse_bonds(castep_file):
  regex_block = re.compile("     Bond                     Population      Length \(A\).*?\n[=]+\n(.*?)\n[=]+", re.M | re.S)
  regex_line = re.compile("\s+([A-Za-z]+)\s+([0-9]+)\s+--\s+([A-Za-z]+)\s+([0-9]+)\s+([0-9\-\.]+)\s+([0-9\-\.]+)\n")

  block = regex_block.findall(castep_file)[0]

  bonds = []
  for s1, i1, s2, i2, population, r in regex_line.findall(block):
    bonds.append(((s1, int(i1)), (s2, int(i2)), float(population), float(r)))

  return bonds

if __name__ == "__main__":
  c = castepy.Cell(open(sys.argv[1]).read())
  bonds = parse_bonds(open(sys.argv[2]).read())

  bs = []
  for (s1, i1), (s2, i2), pop, r in bonds:
    ion1 = c.ions.get_species(s1, i1)
    ion2 = c.ions.get_species(s2, i2)

    if ion1.p[2] < -1.0/6 or ion1.p[2] > 1.0/6:
      continue

    d2, p = ion.least_mirror(ion2.p, ion1.p)
    p = (p[0], p[1], p[2]+1.0)
    if r < 2.0:
      print " ".join(map(str, ion1.p)), " ".join(map(str, p))


  
