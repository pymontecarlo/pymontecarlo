#!/usr/bin/env python
"""
================================================================================
:mod:`limit` -- Stopping condition for a simulation
================================================================================

.. module:: limit
   :synopsis: Stopping condition for a simulation

.. inheritance-diagram:: pymontecarlo.input.limit

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

__all__ = ['TimeLimit',
           'ShowersLimit',
           'UncertaintyLimit']

# Standard library modules.

# Third party modules.
import numpy as np
from pyxray.transition import Transition

# Local modules.
from pymontecarlo.util.parameter import \
    ParameterizedMetaclass, Parameter, TimeParameter, range_validator
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class _Limit(object, metaclass=ParameterizedMetaclass):

    def __str__(self):
        return '%s' % camelcase_to_words(self.__class__.__name__)

class _TransitionLimit(_Limit):

    transition = Parameter(Transition, doc="Transitions for the limit")

    def __init__(self, transition):
        self.transition = transition

class TimeLimit(_Limit):

    time = TimeParameter(range_validator(0, inclusive=False),
                         doc="Simulation time in seconds")

    def __init__(self, time_s):
        self.time_s = time_s

    def __repr__(self):
        return '<TimeLimit(time=%s s)>' % self.time_s

    def __str__(self):
        return '%s (time=%s s)' % \
            (camelcase_to_words(self.__class__.__name__), self.time_s)

class ShowersLimit(_Limit):

    showers = Parameter(np.int, range_validator(1),
                        doc='Number of electron showers')

    def __init__(self, showers):
        self.showers = showers

    def __repr__(self):
        return '<ShowersLimit(showers=%s)>' % self.showers

    def __str__(self):
        return '%s (showers=%s)' % \
            (camelcase_to_words(self.__class__.__name__), self.showers)

class UncertaintyLimit(_TransitionLimit):

    uncertainty = Parameter(np.float, range_validator(0.0, 1.0),
                            doc="Relative uncertainty")

    def __init__(self, transition, uncertainty):
        _TransitionLimit.__init__(self, transition)

        self.uncertainty = uncertainty

    def __repr__(self):
        return '<UncertaintyLimit(%i transitions, uncertainty=%s %%)>' % \
            (len(self.transitions), self.uncertainty * 100.0)

    def __str__(self):
        return '%s (%i transitions, uncertainty=%s %%)' % \
            (camelcase_to_words(self.__class__.__name__),
             len(self.transitions), self.uncertainty * 100.0)
