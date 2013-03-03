#!/usr/bin/env python
"""
================================================================================
:mod:`convolve` -- Perform convolution on photon spectrum
================================================================================

.. module:: convolve
   :synopsis: Perform convolution on photon spectrum

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math

# Third party modules.

# Local modules.

# Globals and constants variables.

def fwhm_sili(energy):
    return math.sqrt(7849.255 + 2.237253 * energy)

def fwhm_cdte(energy):
    return math.sqrt(64.5 * energy)

def fwhm_nai(energy):
    return 40.0 * math.sqrt(energy) + 0.028 * energy

def efficiency_range(energy_min, energy_max, value=1.0):
    def efficiency(energy):
        if energy_min <= energy <= energy_max:
            return value
        else:
            return 0.0

    return efficiency
