#!/usr/bin/env python
"""
================================================================================
:mod:`helper` -- Small routines to help change values in options
================================================================================

.. module:: helper
   :synopsis: Small routines to help change values in options

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.parameter import iter_values
from pymontecarlo.options.detector import _EnergyDetector

# Globals and constants variables.

def replace_material(options, old_material, new_material):
    """
    Replaces all occurrences of *old_material* with *new_material* in the
    options.

    :arg options: options
    :arg old_material: material to be replaced
    :arg new_material: new material

    :return: number of occurrences
    """
    count = 0

    for body in options.geometry.get_bodies():
        if body.material is old_material:
            body.material = new_material
            count += 1

    return count

def ensure_emax(options, emax=None):
    """
    Ensures that the beam energy and all upper energy limits of the detectors
    is set to *emax*.
    If *emax* is ``None``, the beam energy from the options is used.

    :arg options: options
    :arg emax: maximum energy in eV

    :return: *emax*
    """
    if emax is None:
        emax = options.beam.energy

    options.beam.energy = emax

    for detector in options.detectors.matches(_EnergyDetector).values():
        detector.limits = (detector.limits[0], emax)

    return emax

def expand(options):
    """

    """
    prm_values = {}

    for baseobj, name, value in iter_values(options):
        prm_values.setdefault((baseobj, name), []).append(value)

    print prm_values
