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
from pymontecarlo.util.xmlutil import XMLIO, objectxml

# Globals and constants variables.

class _CompositionRule(objectxml):

    def __init__(self, z):
        self._z = z

    def __repr__(self):
        return '<%s(%i)>' % (self.__class__.__name__, self.z)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        z = int(element.get('z'))

        return cls(z)

    def __savexml__(self, element, *args, **kwargs):
        element.set('z', str(self.z))

    @property
    def z(self):
        return self._z

    def update(self, composition):
        """
        Updates the specified composition for the selected element.
        """
        raise NotImplementedError

class ElementByDifferenceRule(_CompositionRule):

    def update(self, composition):
        if self.z in composition:
            composition.pop(self.z)

        total = min(sum(composition.values()), 1.0)

        if total < 1.0:
            composition[self.z] = 1.0 - total

XMLIO.register('{http://pymontecarlo.sf.net}elementByDifferenceRule', ElementByDifferenceRule)

class FixedElementRule(_CompositionRule):
    """
    Fixed weight fraction for an element.
    """

    def __init__(self, z, wf):
        _CompositionRule.__init__(self, z)

        if wf <= 0.0 or wf > 1.0:
            raise ValueError, 'Weight fraction must be between ]0.0, 1.0]'
        self._wf = wf

    def __repr__(self):
        return '<%s(%i @ %s wt%%)>' % \
                    (self.__class__.__name__, self.z, self._wf * 100.0)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        z = int(element.get('z'))
        wf = float(element.get('weightFraction'))

        return cls(z, wf)

    def __savexml__(self, element, *args, **kwargs):
        _CompositionRule.__savexml__(self, element, *args, **kwargs)
        element.set('weightFraction', str(self.weightfraction))

    @property
    def weightfraction(self):
        return self._wf

    def update(self, composition):
        composition[self.z] = self.weightfraction

XMLIO.register('{http://pymontecarlo.sf.net}fixedElementRule', FixedElementRule)
