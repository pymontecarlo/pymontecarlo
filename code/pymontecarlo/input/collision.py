#!/usr/bin/env python
"""
================================================================================
:mod:`collision` -- Type of particle collisions
================================================================================

.. module:: collision
   :synopsis: Type of particle collisions

.. inheritance-diagram:: pymontecarlo.input.collision

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

class _Collision(object):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return '<%s>' % self._name.title()

    def __str__(self):
        return self._name

    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        return self

DELTA = _Collision('delta') # No interaction

HARD_ELASTIC = _Collision('hard elastic')
HARD_INELASTIC = _Collision('hard inelastic')
HARD_BREMSSTRAHLUNG_EMISSION = _Collision('hard bremsstrahlung emission')
INNERSHELL_IMPACT_IONISATION = _Collision('inner shell impact ionisation')
COHERENT_RAYLEIGH_SCATTERING = _Collision('coherent Rayleigh scattering')
INCOHERENT_COMPTON_SCATTERING = _Collision('incoherent Compton scattering')
PHOTOELECTRIC_ABSORPTION = _Collision('photoelectric absorption')
ELECTRON_POSITRON_PAIR_PRODUCTION = _Collision('electron-positron pair production')
ANNIHILATION = _Collision('annihilation')

COLLISIONS = \
    frozenset([DELTA, HARD_ELASTIC, HARD_INELASTIC, HARD_BREMSSTRAHLUNG_EMISSION,
               INNERSHELL_IMPACT_IONISATION, COHERENT_RAYLEIGH_SCATTERING,
               INCOHERENT_COMPTON_SCATTERING, PHOTOELECTRIC_ABSORPTION,
               ELECTRON_POSITRON_PAIR_PRODUCTION, ANNIHILATION])

