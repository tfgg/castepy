# Take moments of a point distribution
import numpy

def dipole(points):
  points = map(numpy.array, points)
  mean = sum(points) / len(points)

  #points = [p - mean for p in points]

  d = len(points[0])

  accum = numpy.array([0.0]*d)
  for point in points:
    accum += point

  return accum

def delta(i,j):
  if i == j: return 1
  else: return 0

def quadrupole(points, weights=None):
  points = map(numpy.array, points)
  mean = sum(points) / len(points)

  if weights is None:
    weights = [1.0 for point in points]
  
  points = [p - mean for p in points]

  d = len(points[0])

  Q = numpy.array([[0.0] * d]*d)
  for i in range(d):
    for j in range(d):
      for weight, point in zip(weights, points):
        Q[i,j] += weight * (3.0*point[i] * point[j] - delta(i,j) * point[i]**2)

  return Q

if __name__ == "__main__":
  points1 = [(1.0, 0.0, 0.0)]
  points2 = [(1.0, 1.0, 0.0), (-1.0, -1.0, 0.0)]

  print dipole(points1)
  print quadrupole(points1)
  
  print dipole(points2)
  print quadrupole(points2)
