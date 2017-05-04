"""
Electron range calculations
"""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.

# Globals and constants variables.

def kanaya_okayama(composition, energy):
    """
    Returns the electron range (in meters).

    :arg composition: composition in weight fraction.
        The composition is specified by a dictionary.
        The keys are the atomic numbers and the values are the weight fractions
        between ]0.0, 1.0].
    :type composition: :class:`dict`

    :arg energy: beam energy in eV
    """
    r = 0.0;

    for z, fraction in composition.items():
        dr = (0.0276 * pyxray.element_atomic_weight(z) * (energy / 1000.0) ** 1.67) / \
            (z ** 0.89 * pyxray.element_mass_density_g_per_cm3(z))
        r += fraction / (dr * 1e-6)

    return 1.0 / r;

