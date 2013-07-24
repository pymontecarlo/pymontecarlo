#!/usr/bin/env python
"""
================================================================================
:mod:`body` -- PENELOPE body for geometry
================================================================================

.. module:: body
   :synopsis: PENELOPE body for geometry

.. inheritance-diagram:: pymontecarlo.program._penelope.input.body

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.input.body import Body as _Body, Layer as _Layer
from pymontecarlo.input.parameter import \
    UnitParameter, FrozenParameter, ParameterizedMutableSet, _Validator
from pymontecarlo.input.xmlmapper import \
    mapper, ParameterizedAttribute, ParameterizedElementSet, PythonType, UserType
from pymontecarlo.program._penelope.input.interactionforcing import InteractionForcing


# Globals and constants variables.

class _MaximumStepLengthValidator(_Validator):

    def validate(self, value):
        if value > 1e20:
            warnings.warn('Maximum step length set to maximum value: 1e20')
            value = 1e20
        if value < 0:
            raise ValueError, "Length (%s) must be greater than 0.0." % value
        return value

class Body(_Body):

    maximum_step_length = UnitParameter('m', _MaximumStepLengthValidator(),
                                        "Maximum length of an electron trajectory")
    interaction_forcings = FrozenParameter(ParameterizedMutableSet,
                                           "Interaction forcing(s)")

    def __init__(self, material, maximum_step_length_m=1e20):
        _Body.__init__(self, material)

        self.maximum_step_length_m = maximum_step_length_m
        self.interaction_forcings.clear()

    def __repr__(self):
        return '<Body(material=%s, %i interaction forcing(s), dsmax=%s m)>' % \
            (str(self.material), len(self.interaction_forcings), self.maximum_step_length_m)

mapper.register(Body, '{http://pymontecarlo.sf.net/penelope}body',
                ParameterizedAttribute('maximum_step_length_m', PythonType(float), 'maximum_step_length'),
                ParameterizedElementSet('interaction_forcings', UserType(InteractionForcing)))

class Layer(Body, _Layer):

    def __init__(self, material, thickness, maximum_step_length_m=None):
        _Layer.__init__(self, material, thickness)

        if maximum_step_length_m is None:
            maximum_step_length_m = thickness / 10.0
        Body.__init__(self, material, maximum_step_length_m)

mapper.register(Layer, '{http://pymontecarlo.sf.net/penelope}layer')
