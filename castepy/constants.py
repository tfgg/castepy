import math

Z = {u'H': 1, u'Ru': 44, u'Re': 75, u'Ra': 88, u'Rb': 37, u'Rn': 86, u'Rh': 45, u'Be': 4, u'Ba': 56, u'Bi': 83, u'Br': 35, u'P': 15, u'Os': 76, u'Ge': 32, u'Gd': 64, u'Ga': 31, u'Pr': 59, u'Pt': 78, u'C': 6, u'Pb': 82, u'Pa': 91, u'Pd': 46, u'Cd': 48, u'Po': 84, u'Pm': 61, u'Ho': 67, u'Hf': 72, u'Hg': 80, u'He': 2, u'Mg': 12, u'K': 19, u'Mn': 25, u'O': 8, u'S': 16, u'W': 74, u'Zn': 30, u'Eu': 63, u'Zr': 40, u'Er': 68, u'Ni': 28, u'Na': 11, u'Nb': 41, u'Nd': 60, u'Ne': 10, u'Fr': 87, u'Fe': 26, u'B': 5, u'F': 9, u'Sr': 38, u'N': 7, u'Kr': 36, u'Si': 14, u'Sn': 50, u'Sm': 62, u'V': 23, u'Sc': 21, u'Sb': 51, u'Se': 34, u'Co': 27, u'Cl': 17, u'Ca': 20, u'Ce': 58, u'Xe': 54, u'Tm': 69, u'Cs': 55, u'Cr': 24, u'Cu': 29, u'La': 57, u'Li': 3, u'Tl': 81, u'Lu': 71, u'Th': 90, u'Ti': 22, u'Te': 52, u'Tb': 65, u'Tc': 43, u'Ta': 73, u'Yb': 70, u'Dy': 66, u'I': 53, u'U': 92, u'Y': 39, u'Ac': 89, u'Ag': 47, u'Ir': 77, u'Al': 13, u'As': 33, u'Ar': 18, u'Au': 79, u'At': 85, u'In': 49, u'Mo': 42, u'Am': 95, u'Pu': 94, u'Cm': 96}

# CODATA2006
speed_light_si = 299792458.0
mu_0_si = 4.0*math.pi*1e-7
epsilon_0_si = 1.0/(mu_0_si*speed_light_si**2)
planck_si = 6.62606896e-34
elementary_charge_si = 1.602176487e-19
electron_mass_si = 9.10938215e-31
proton_mass_si = 1.672621637e-27
electron_gyromagnetic_ratio_si = 1.76085977e11
avogadro_si = 6.02214179e23
molar_gas_si = 8.314472
hbar_si = planck_si / (2.0 * math.pi)
fine_structure_si = elementary_charge_si**2/(4.0*math.pi*epsilon_0_si*hbar_si*speed_light_si)
boltzmann_si = molar_gas_si/avogadro_si
amu_si = 1e-3/avogadro_si
