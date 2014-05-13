#!/usr/bin/env python
"""
================================================================================
:mod:`electron_range` -- Electron range calculations
================================================================================

.. module:: electron_range
   :synopsis: Electron range calculations

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
import pyxray.element_properties as ep

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
        dr = (0.0276 * (ep.atomic_mass_kg_mol(z) * 1000.0) * (energy / 1000.0) ** 1.67) / \
            (z ** 0.89 * (ep.mass_density_kg_m3(z) / 1000.0))
        r += fraction / (dr * 1e-6)

    return 1.0 / r;

