#!/usr/bin/env python
"""
================================================================================
:mod:`particle` -- Type of particles
================================================================================

.. module:: particle
   :synopsis: Type of particles

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

__all__ = ['ELECTRON',
           'PHOTON',
           'POSITRON',
           'PARTICLES']

# Standard library modules.
from functools import total_ordering

# Third party modules.

# Local modules.

# Globals and constants variables.

@total_ordering
class _Particle(object):
    def __init__(self, name, index, charge):
        self._name = name
        self._index = index
        self._charge = charge

    def __repr__(self):
        return '<%s>' % self._name.upper()

    def __str__(self):
        return self._name

    def __int__(self):
        return self._index

    def __eq__(self, other):
        return self._index == other._index

    def __lt__(self, other):
        return self._index < other._index

    def __hash__(self):
        return hash((self.__class__, self._index))

    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        return self

    @property
    def charge(self):
        return self._charge

ELECTRON = _Particle('electron', 1, -1) # : Electron particle
PHOTON = _Particle('photon', 2, 0) # : Photon particle
POSITRON = _Particle('positron', 3, +1) # : Positron particle

PARTICLES = frozenset([ELECTRON, PHOTON, POSITRON])
