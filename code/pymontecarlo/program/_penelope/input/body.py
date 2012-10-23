#!/usr/bin/env python
"""
================================================================================
:mod:`body` -- PENELOPE body for geometry
================================================================================

.. module:: body
   :synopsis: PENELOPE body for geometry

.. inheritance-diagram:: pymontecarlo.program.penelope.input.body

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.
from lxml.etree import Element

# Local modules.
from pymontecarlo.input.body import Body as _Body, Layer as _Layer
from pymontecarlo.input.option import Option
from pymontecarlo.program._penelope.input.interactionforcing import InteractionForcing
from pymontecarlo.util.xmlutil import XMLIO

# Globals and constants variables.

class Body(_Body, Option):
    def __init__(self, material, maximum_step_length_m=1e20):
        Option.__init__(self)
        _Body.__init__(self, material)

        self._props['interaction forcings'] = set()
        self.maximum_step_length_m = maximum_step_length_m

    def __repr__(self):
        return '<Body(material=%s, %i interaction forcing(s), dsmax=%s m)>' % \
            (str(self.material), len(self.interaction_forcings), self.maximum_step_length_m)

    @classmethod
    def __loadxml__(cls, element, material=None, *args, **kwargs):
        body = _Body.__loadxml__(element, material, *args, **kwargs)
        maximum_step_length = float(element.get('maximumStepLength'))

        obj = cls(body.material, maximum_step_length)

        children = list(element.find("interactionForcings"))
        for child in children:
            obj.interaction_forcings.add(InteractionForcing.from_xml(child))

        return obj

    def __savexml__(self, element, *args, **kwargs):
        _Body.__savexml__(self, element, *args, **kwargs)

        child = Element("interactionForcings")
        for intforce in self.interaction_forcings:
            child.append(intforce.to_xml())
        element.append(child)

        element.set('maximumStepLength', str(self.maximum_step_length_m))

    @property
    def interaction_forcings(self):
        """
        Set of interaction forcings.
        Use :meth:`add` to add an interaction forcing to this body.
        """
        return self._props['interaction forcings']

    @property
    def maximum_step_length_m(self):
        """
        Maximum length of an electron trajectory in this body (in meters).
        """
        return self._props['maximum step length']

    @maximum_step_length_m.setter
    def maximum_step_length_m(self, length):
        if length < 0 or length > 1e20:
            raise ValueError, "Length (%s) must be between [0, 1e20]." % length
        self._props['maximum step length'] = length

XMLIO.register('{http://pymontecarlo.sf.net/penelope}body', Body)

class Layer(Body, _Layer):
    def __init__(self, material, thickness, maximum_step_length_m=None):
        _Layer.__init__(self, material, thickness)

        if maximum_step_length_m is None:
            maximum_step_length_m = thickness / 10.0
        Body.__init__(self, material, maximum_step_length_m)

    @classmethod
    def __loadxml__(cls, element, material=None, thickness=None, *args, **kwargs):
        layer = _Layer.__loadxml__(element, material, thickness, *args, **kwargs)
        body = Body.__loadxml__(element, material, *args, **kwargs)

        layer = cls(layer.material, layer.thickness_m, body.maximum_step_length_m)

        for intforce in body.interaction_forcings:
            layer.interaction_forcings.add(intforce)

        return layer

    def __savexml__(self, element, *args, **kwargs):
        Body.__savexml__(self, element, *args, **kwargs)
        _Layer.__savexml__(self, element, *args, **kwargs)

XMLIO.register('{http://pymontecarlo.sf.net/penelope}layer', Layer)
