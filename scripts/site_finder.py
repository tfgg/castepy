#!python

import pickle

from kmeans.kmeans import kmeans, classify
from castepy.cell import Cell
import sys
import numpy
from collections import Counter

cell = Cell(open(sys.argv[1]).read())
s = sys.argv[2]
k = int(sys.argv[3])

points = []
ions = []
ion_index = {}

#atomic_number = 

pfile = open("points.dat", "w+")
meanfiles = open("means.dat", "w+")

for ion in cell.ions.get_species(s):
  neighs = cell.neighbours(ion.p)[1:20]

  invec = [r for ion2, r, p in neighs] + [ord(ion2.s[0]) for ion2, _, _ in neighs]
  invec = invec[:2]

  points.append(numpy.array(invec))
  ions.append(ion)
  ion_index[(ion.s, ion.i)] = len(ions)-1

site_votes = dict(((ion.s, ion.i), Counter()) for ion in ions)

for i in range(1):
  print >>sys.stderr, "Try %d" % i

  means = kmeans(points, k, 1e-12)

  for mean in means:
    print >>meanfiles, " ".join(map(str,mean))

  #for mean in means:
  #  print mean

  classification = classify(points, means)
  

  print classification

  sites = {('F', 13): 'F1',
           ('F', 1): 'F2',
           ('F', 9): 'F3',
           ('F', 25): 'F4',
           ('F', 21): 'F5',}

  site_map = {}
  for index, site_name in sites.items():
    site_class = classification[ion_index[index]]
    site_map[site_class] = site_name

  for i, mean_index in enumerate(classification):
    site_votes[(ions[i].s, ions[i].i)][site_map[mean_index]] += 1

ion_site_map = {}

for index, counter in sorted(site_votes.items(), key=lambda (i,c): i):
  ion_site_map[index] = counter.most_common(1)[0][0]
  
  print >>pfile, ion_site_map[index], " ".join(map(str,points[ion_index[index]]))

print pickle.dumps(ion_site_map)

