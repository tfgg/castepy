import re
import numpy
import math

from collections import Counter

from castepy.atoms import AtomsView
from castepy.atom import Atom

class Cell:
    class LatticeNotImplemented(Exception): pass
    class LatticeWrongShape(Exception): pass

    def __init__(self, cell_file=None, **kwargs):
        self.blocks = {}
        self.other = []
        self.otherdict = {}

        self.ions = None 

        if cell_file is not None:
            self.parse_cell(cell_file)

        if 'lattice' in kwargs:
          self.lattice_units = "ang"
          self.lattice_type = "LATTICE_CART"
          self.lattice = numpy.array(kwargs['lattice'])
          self.ions.lattice = self.lattice

          self.ions_units = "ang"
          self.ions_type = "POSITIONS_ABS"
          self.basis = numpy.array([[1.0, 0.0, 0.0],
                                    [0.0, 1.0, 0.0],
                                    [0.0, 0.0, 1.0]])

    def parse_cell(self, cell):
        block_re = re.compile(r"%block (.*?)\n(.*?\n{0,})%endblock (.*?)\n", re.I | re.S | re.M)

        # Fix any windows line endings
        cell = cell.replace("\r\n", "\n")
        blocks = block_re.findall(cell)
        
        for name, content, _ in blocks:
            unclean_lines = content.split('\n')
            lines = []
            for line in unclean_lines:
                line_clean = line.strip()
                if len(line_clean) > 0:
                    lines.append(line_clean)
            self.blocks[name.upper()] = lines

        cell_sans_blocks = block_re.sub("", cell)
        other = re.split("\n\s{0,}", cell_sans_blocks, re.S | re.M)
        for o in other:
            o_s = o.strip()
            if len(o_s) > 0:
                self.other.append(o_s)
                
                o_split = re.split("[\s:]+", o_s, maxsplit=1)

                if len(o_split) == 2:
                    self.otherdict[o_split[0]] = o_split[1]

        self.parse_lattice()
        self.parse_ions()

    def parse_lattice(self):
        self.lattice_type = None
        for block_name in self.blocks:
          if 'LATTICE_' in block_name:
            self.lattice_type = block_name

        if self.lattice_type is None:
          return

        self.lattice_units = "ang"
        
        lattice = []
        if self.lattice_type == 'LATTICE_CART':
          for line in self.blocks[self.lattice_type]:
            lsplit = line.split()

            if len(lsplit) == 3:
              lattice.append((float(lsplit[0]),
                              float(lsplit[1]),
                              float(lsplit[2]),))
            elif len(lsplit) == 1:
              self.lattice_units = lsplit[0]
        else:
          raise self.LatticeNotImplemented("%s not implemented in parser" % self.lattice_type)

        self.lattice = numpy.array(lattice)

        if self.lattice.shape != (3,3):
          raise self.LatticeWrongShape("Lattice vectors given not 3x3")

    def parse_ions(self):
        self.ions_type = None

        if 'POSITIONS_ABS' in self.blocks:
          self.ions_type = 'POSITIONS_ABS'
          self.basis = numpy.array([[1.0, 0.0, 0.0],
                                    [0.0, 1.0, 0.0],
                                    [0.0, 0.0, 1.0]])
        elif 'POSITIONS_FRAC' in self.blocks:
          self.ions_type = 'POSITIONS_FRAC'
          self.basis = self.lattice

        if self.ions_type is None:
          return

        convert = False # Dont convert frac to cart
        if self.ions_type == 'POSITIONS_FRAC':
          convert = True

        atoms = []

        index_counter = Counter()

        self.ions_units = None
        for line in self.blocks[self.ions_type]: # Include positions frac
          lsplit = line.split()

          if len(lsplit) == 4:
            s, x, y, z = lsplit
            position = (float(x), float(y), float(z))

            sl = s.split(":")

            species = sl[0]

            # Atoms are 1-indexed to match castep.
            index_counter[species] += 1
            index = index_counter[species]

            if len(sl) > 1:
              label = sl[1]
            else:
              label = species

            if convert:
              position = numpy.dot(self.basis.T, position)

            atoms.append(Atom(species, index, position, label))

          elif len(lsplit) == 1:
            self.ions_units = lsplit[0]

        if self.ions_units is None:
          self.ions_units = 'ang'

        # If we've converted, change the basis
        if convert:
          self.ions_type = 'POSITIONS_ABS'
          self.basis = numpy.array([[1.0, 0.0, 0.0],
                                    [0.0, 1.0, 0.0],
                                    [0.0, 0.0, 1.0]])

        self.ions = AtomsView(atoms, self.lattice)

    def regen_ion_block(self):
        for type in ['POSITIONS_ABS', 'POSITIONS_FRAC']: # Clear out any other ion blocks
          if type in self.blocks:
            del self.blocks[type]

        self.blocks[self.ions_type] = [self.ions_units] + ["{} {:f} {:f} {:f}".format(atom.species, atom.position[0], atom.position[1], atom.position[2]) for atom in self.ions]

    def regen_lattice_block(self):
        self.blocks[self.lattice_type] = [self.lattice_units] + ["{:f} {:f} {:f}".format(a,b,c) for a,b,c in self.ions.lattice]

    def jcoupling_shift_origin(self):
        """ Hack to move the perturbing NMR nucleus onto the origin """
        if 'jcoupling_site' not in self.otherdict:
          j_site = raw_input("Specify the j-coupling site: ").split()
          self.other.append("jcoupling_site: " + " ".join(j_site))
        else: 
          j_site = self.otherdict['jcoupling_site'].split()
        
        j_site_ion = self.ions.get_species(j_site[0], int(j_site[1]))
        self.ions.translate_origin(j_site_ion.p) 

    def make_unique_ions(self):
        """ Generate a unique set of the ions, fix duplicates """
        ions = dict()

        for ion in self.ions:
          trunc_pos = (round(ion[1][0], 2), round(ion[1][1], 2), round(ion[1][2], 2))
          if trunc_pos in ions:
            ions[trunc_pos].append(ion)
          else:
            ions[trunc_pos] = [ion]

        ions_prime = []
        for trunc_pos, ions in sorted(ions.items()):
          #print trunc_pos, len(ions)
          ions_prime.append(ions[0])

        #print len(self.ions)
        #print len(ions_prime)
        self.ions = ions_prime
        self.ion_index = self.make_ion_index()

        self.regen_ion_block()
   
    # Geometric routines
    def closest(self, q):
      """
        Find the ion closest to q, accounting for cyclic coordinates.
      """

      min_d2 = None
      min_ion = None
      min_p = None
     
      for ion in self.ions:
        d2,p = least_mirror(ion.p, q, self.basis, self.ions.lattice)

        if min_d2 is None or d2 < min_d2:
          min_d2 = d2
          min_ion = ion
          min_p = p

      return (min_ion, math.sqrt(min_d2), min_p)

    def least_mirror(self, p, q):
      return least_mirror(p, q, self.ions.basis, self.ions.lattice)

    def neighbours(self, q, max_dist=None, above_index=0, species=None):
      """
        Return neighbours of q in distance order, for easy slicing
      """
    
      ions = []
      for i in range(above_index, len(self.ions)):
        ion = self.ions[i]

        d2, p = self.least_mirror(ion.p, q)

        if (max_dist is None or d2 < max_dist**2) and (species is None or ion.s in species):
          ions.append((ion, math.sqrt(d2), p))
    
      return sorted(ions, key=lambda (ion,d,p): d)

    def __str__(self):
        self.regen_ion_block()
        self.regen_lattice_block()
        s  = ""
        for name, lines in self.blocks.items():
            s += "%%block %s\n" % name
            s += "\n".join(lines)
            s += "\n%%endblock %s\n\n" % name

        for line in self.other:
            s += "%s\n" % line

        return s

