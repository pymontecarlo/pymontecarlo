#!/usr/bin/env python
"""
================================================================================
:mod:`particle` -- Type of particles
================================================================================

.. module:: particle
   :synopsis: Type of particles

.. inheritance-diagram:: pymontecarlo.input.particle

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

class _Particle(object):
    def __init__(self, name, charge):
        self._name = name
        self._charge = charge

    def __repr__(self):
        return '<%s>' % self._name.upper()

    def __str__(self):
        return self._name

    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        return self

    @property
    def charge(self):
        return self._charge

ELECTRON = _Particle('electron', -1)
PHOTON = _Particle('photon', 0)
POSITRON = _Particle('positron', +1)

PARTICLES = frozenset([ELECTRON, PHOTON, POSITRON])
