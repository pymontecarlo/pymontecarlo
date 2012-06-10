#!/usr/bin/env python
"""
================================================================================
:mod:`rule` -- Rules applied during quantification
================================================================================

.. module:: rule
   :synopsis: Rules applied during quantification

.. inheritance-diagram:: pymontecarlo.analysis.rule

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

class _CompositionRule(object):

    def __init__(self, z):
        self._z = z

    @property
    def z(self):
        return self._z

    def update(self, composition):
        """
        Updates the specified composition for the selected element.
        """
        raise NotImplementedError

class ElementByDifference(_CompositionRule):

    def update(self, composition):
        if self.z in composition:
            composition.pop(self.z)

        total = min(sum(composition.values()), 1.0)

        if total < 1.0:
            composition[self.z] = 1.0 - total

class FixedElement(_CompositionRule):
    """
    Fixed weight fraction for an element.
    """

    def __init__(self, z, wf):
        _CompositionRule.__init__(self, z)
        self._wf = wf

    @property
    def weightfraction(self):
        return self._wf

    def update(self, composition):
        composition[self.z] = self.weightfraction
