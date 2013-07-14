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
from pyxray.transition import Transition

# Local modules.
from pymontecarlo.input.parameter import \
    (ParameterizedMetaClass, Parameter, FrozenParameter, TimeParameter,
     SimpleValidator)
from pymontecarlo.input.xmlmapper import \
    mapper, ParameterizedAttribute, ParameterizedElementSet, UserType, PythonType

# Globals and constants variables.

class _Limit(object):

    __metaclass__ = ParameterizedMetaClass

class _TransitionsLimit(_Limit):

    transitions = FrozenParameter(set, doc="Transitions for the limit")

    def __init__(self, transitions):
        if hasattr(transitions, '__iter__'):
            self.transitions.update(transitions)
        else:
            self.transitions.add(transitions)

mapper.register(_TransitionsLimit, '{http://pymontecarlo.sf.net}_transitionsLimit',
                ParameterizedElementSet('transitions', UserType(Transition)))

_time_validator = SimpleValidator(lambda t: t > 0,
                                  "Time must be greater than 0")

class TimeLimit(_Limit):

    time = TimeParameter(_time_validator, "Simulation time in seconds")

    def __init__(self, time):
        self.time_s = time

    def __repr__(self):
        return '<TimeLimit(time=%s s)>' % self.time_s

mapper.register(TimeLimit, '{http://pymontecarlo.sf.net}timeLimit',
                ParameterizedAttribute('time_s', PythonType(float), 'time'))

_showers_validator = \
    SimpleValidator(lambda s: s >= 1,
                    "Number of showers must be equal or greater than 1")

class ShowersLimit(_Limit):

    showers = Parameter(_showers_validator, 'Number of electron showers')

    def __init__(self, showers):
        self.showers = showers

    def __repr__(self):
        return '<ShowersLimit(showers=%s)>' % self.showers

mapper.register(ShowersLimit, '{http://pymontecarlo.sf.net}showersLimit',
                ParameterizedAttribute('showers', PythonType(long)))

_uncertainty_validator = \
    SimpleValidator(lambda unc: 0.0 < unc < 1.0,
                    'Relative uncertainty must be between [0.0, 1.0]')

class UncertaintyLimit(_TransitionsLimit):
    
    uncertainty = Parameter(_uncertainty_validator, "Relative uncertainty")

    def __init__(self, transitions, uncertainty):
        _TransitionsLimit.__init__(self, transitions)

        self.uncertainty = uncertainty

    def __repr__(self):
        return '<UncertaintyLimit(%i transitions, uncertainty=%s %%)>' % \
            (len(self.transitions), self.uncertainty * 100.0)

mapper.register(UncertaintyLimit, '{http://pymontecarlo.sf.net}uncertaintyLimit',
                ParameterizedAttribute('uncertainty', PythonType(float)))
