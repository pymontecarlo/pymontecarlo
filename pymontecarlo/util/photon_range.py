#!/usr/bin/env python
"""
================================================================================
:mod:`photon_range` -- Estimate of electron range
================================================================================

.. module:: photon_range
   :synopsis: Estimate of electron range

.. inheritance-diagram:: pymontecarlo.util.photon_range

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

def photon_range(e0, material, transition):
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
    :arg transition: x-ray line transition
    
    :return: photon range (in meters)
    """
    if transition.z not in material.composition:
        raise ValueError('%s is not in material' % transition.symbol)
    if transition.energy_eV > e0:
        return 0.0

    z = transition.z
    ck = 43.04 + 1.5 * z + 5.4e-3 * z ** 2
    cn = 1.755 - 7.4e-3 * z + 3.0e-5 * z ** 2
    density = material.density_g_cm3

    e0 = e0 / 1e3
    ec = transition.energy_eV / 1e3

    return ck / density * (e0 ** cn - ec ** cn) * 1e-9
