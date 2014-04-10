#!python
import re
import sys, os
import math

force_block = re.compile(r" \*+ Forces \*+\n \*\s+\*\n \*\s+Cartesian components \(eV\/A\)\s+\*\n \* \-+ \*\n(.*?)\n \*{2,}", re.S)
atom_line = re.compile(" \* ([A-Za-z]+)\s+([0-9]+)\s+([0-9\.\-E\(\)a-z\']+)\s+([0-9\.\-E\(\)a-z\']+)\s+([0-9\.\-E\(\)a-z\']+)")

def find_atoms(block):
  atoms = []
  for s, i, x, y, z in atom_line.findall(block):
    i = int(i)
      
    x_consd = "(cons'd)" in x
    x = float(x.replace("(cons'd)", ""))

    y_consd = "(cons'd)" in y
    y = float(y.replace("(cons'd)", ""))
    
    z_consd = "(cons'd)" in z
    z = float(z.replace("(cons'd)", ""))


    norm = math.sqrt(x**2 + y**2 + z**2)

    atoms.append((s, i, x, y, z, x_consd, y_consd, z_consd, norm))

  return atoms

if __name__ == "__main__":
  c = open(sys.argv[1]).read()
  blocks = force_block.findall(c)

  atoms = sorted(find_atoms(blocks[len(blocks)-1]),
                 key=lambda (s,i,x,y,z,_x,_y,_z,n): n,
                 reverse=True)

  for s, i, x, y, z, x_, y_, z_, n in atoms[:10]:
    print n, "->", s, i, x, y, z
