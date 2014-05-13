#!/usr/bin/env python
"""
================================================================================
:mod:`collision` -- Type of particle collisions
================================================================================

.. module:: collision
   :synopsis: Type of particle collisions

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

__all__ = ['NO_COLLISION',
           'DELTA',
           'SOFT_EVENT',
           'HARD_ELASTIC',
           'HARD_INELASTIC',
           'HARD_BREMSSTRAHLUNG_EMISSION',
           'INNERSHELL_IMPACT_IONISATION',
           'COHERENT_RAYLEIGH_SCATTERING',
           'INCOHERENT_COMPTON_SCATTERING',
           'PHOTOELECTRIC_ABSORPTION',
           'ELECTRON_POSITRON_PAIR_PRODUCTION',
           'ANNIHILATION',
           'COLLISIONS']

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

class _Collision(object):
    def __init__(self, name, index):
        self._name = name
        self._index = index

    def __repr__(self):
        return '<%s>' % self._name.title()

    def __str__(self):
        return self._name

    def __int__(self):
        return self._index

    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        return self

NO_COLLISION = _Collision('no collision', -1)
DELTA = _Collision('delta', 0) # No interaction

SOFT_EVENT = _Collision('artificial soft event', 1)
HARD_ELASTIC = _Collision('hard elastic', 2)
HARD_INELASTIC = _Collision('hard inelastic', 3)
HARD_BREMSSTRAHLUNG_EMISSION = _Collision('hard bremsstrahlung emission', 4)
INNERSHELL_IMPACT_IONISATION = _Collision('inner shell impact ionisation', 5)
COHERENT_RAYLEIGH_SCATTERING = _Collision('coherent Rayleigh scattering', 6)
INCOHERENT_COMPTON_SCATTERING = _Collision('incoherent Compton scattering', 7)
PHOTOELECTRIC_ABSORPTION = _Collision('photoelectric absorption', 8)
ELECTRON_POSITRON_PAIR_PRODUCTION = _Collision('electron-positron pair production', 9)
ANNIHILATION = _Collision('annihilation', 10)

COLLISIONS = \
    frozenset([NO_COLLISION, DELTA, SOFT_EVENT, HARD_ELASTIC, HARD_INELASTIC,
               HARD_BREMSSTRAHLUNG_EMISSION, INNERSHELL_IMPACT_IONISATION,
               COHERENT_RAYLEIGH_SCATTERING, INCOHERENT_COMPTON_SCATTERING,
               PHOTOELECTRIC_ABSORPTION, ELECTRON_POSITRON_PAIR_PRODUCTION,
               ANNIHILATION])
