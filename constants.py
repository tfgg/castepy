import math

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
