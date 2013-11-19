import sys
import re

re_num_kpoints = re.compile('Number of k-points\s+([0-9]+)')
re_num_spins = re.compile('Number of spin components\s+([0-9]+)')
re_num_electrons = re.compile('Number of electrons\s+([0-9\.]+)')
re_num_eigenvalues = re.compile('Number of eigenvalues\s+([0-9]+)')
re_fermi_energy = re.compile('Fermi energy \(in atomic units\)\s+([\-0-9\.]+)')

re_unit_cell = re.compile('Unit cell vectors\n\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)\n\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)\n\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)\n')


re_kpoint = re.compile('K-point\s+([0-9]+)\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)\n(.*)', re.M | re.S)
re_spin = re.compile('Spin component\s+([0-9]+)\n(.*)', re.M | re.S)

def parse_bands(bands):
  num_kpoints = int(re_num_kpoints.findall(bands)[0])
  num_spins = int(re_num_spins.findall(bands)[0])
  num_electrons = float(re_num_electrons.findall(bands)[0])
  num_eigenvalues = int(re_num_eigenvalues.findall(bands)[0])
  fermi_energy = float(re_fermi_energy.findall(bands)[0])
  unit_cell = map(float,re_unit_cell.findall(bands)[0])
  kpoints = re_kpoint.findall(bands)


  result = {'fermi_energy': fermi_energy,
            'unit_cell': [unit_cell[:3], unit_cell[3:6], unit_cell[6:]],
            'num_electrons': num_electrons,
            'num_eigenvalues': num_eigenvalues,
            'kpoints': [],}

  for kpoint in kpoints:
    idx, kx, ky, kz, weight, spins_bands = kpoint

    idx = int(idx)
    kx, ky, kz = float(kx), float(ky), float(kz)
    weight = float(weight)

    spin_bands = re_spin.findall(spins_bands)


    kpoint_result = {'index': idx,
                     'weight': weight,
                     'k': [kx, ky, kz],
                     'spins': [],}

    for spin, bands in spin_bands:
      spin_result = {'index': int(spin),
                     'bands': map(float, bands.split())}

      kpoint_result['spins'].append(spin_result)

    result['kpoints'].append(kpoint_result)


  return result

if __name__ == "__main__":
  result = parse_bands(open(sys.argv[1]).read())

  print result
