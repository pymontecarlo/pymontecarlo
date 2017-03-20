"""
Estimate of electron range
"""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.

# Globals and constants variables.

def photon_range(e0, material, xrayline, reference=None):
    """
    This function returns the generated photon range in *material* at
    incident electron energy *e0* for a characteristic x ray line *transition*.

    Reference:
    Hovington, P., Drouin, D., Gauvin, R. & Joy, D.C. (1997).
    Parameterization of the range of electrons at low energy using
    the CASINO Monte Carlo program. Microsc Microanal 3(suppl.2),
    885–886.
    
    :arg e0: incident electron energy (in eV)
    :arg material: material
    :arg xrayline: x-ray line
    
    :return: photon range (in meters)
    """
    z = xrayline.atomic_number
    if z not in material.composition:
        raise ValueError('{} is not in material'.format(xrayline))

    if xrayline.is_xray_transitionset():
        energy_eV = pyxray.xray_transitionset_energy_eV(*xrayline, reference=reference)
    else:
        energy_eV = pyxray.xray_transition_energy_eV(*xrayline, reference=reference)
    if energy_eV > e0:
        return 0.0

    ck = 43.04 + 1.5 * z + 5.4e-3 * z ** 2
    cn = 1.755 - 7.4e-3 * z + 3.0e-5 * z ** 2
    density = material.density_g_per_cm3

    e0 = e0 / 1e3
    ec = energy_eV / 1e3

    return ck / density * (e0 ** cn - ec ** cn) * 1e-9
