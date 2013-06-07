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

# Local modules.
#from pymontecarlo.input.option import Option
#from pymontecarlo.util.xmlutil import XMLIO
from pymontecarlo.input.parameter import \
    ParameterizedMetaClass, Parameter, TimeParameter, SimpleValidator

# Globals and constants variables.

class _TransitionsLimit(object):

    __metaclass__ = ParameterizedMetaClass

    transitions = Parameter(doc="Transitions for the limit")

    def __init__(self, transitions):
        self.transitions = set()
        self.__parameters__['transitions'].freeze(self)

        if hasattr(transitions, '__iter__'):
            self.transitions.update(transitions)
        else:
            self.transitions.add(transitions)

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        transitions = set()
#        for child in list(element):
#            transitions.add(XMLIO.from_xml(child, *args, **kwargs))
#
#        return cls(transitions)
#
#    def __savexml__(self, element, *args, **kwargs):
#        for transition in self.transitions:
#            element.append(transition.to_xml())

_time_validator = SimpleValidator(lambda t: t > 0,
                                  "Time must be greater than 0")

class TimeLimit(object):

    __metaclass__ = ParameterizedMetaClass

    time = TimeParameter(_time_validator, "Simulation time in seconds")

    def __init__(self, time):
        self.time_s = time

    def __repr__(self):
        return '<TimeLimit(time=%s s)>' % self.time_s

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        time = long(element.get('time'))
#        return cls(time)
#
#    def __savexml__(self, element, *args, **kwargs):
#        element.set('time', str(self.time_s))

#XMLIO.register('{http://pymontecarlo.sf.net}timeLimit', TimeLimit)

_showers_validator = \
    SimpleValidator(lambda s: s >= 1,
                    "Number of showers must be equal or greater than 1")

class ShowersLimit(object):

    __metaclass__ = ParameterizedMetaClass

    showers = Parameter(_showers_validator, 'Number of electron showers')

    def __init__(self, showers):
        self.showers = showers

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        showers = long(element.get('showers'))
#        return cls(showers)
#
#    def __savexml__(self, element, *args, **kwargs):
#        element.set('showers', str(self.showers))

    def __repr__(self):
        return '<ShowersLimit(showers=%s)>' % self.showers

#XMLIO.register('{http://pymontecarlo.sf.net}showersLimit', ShowersLimit)

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

#    @classmethod
#    def __loadxml__(cls, element, *args, **kwargs):
#        transitions = \
#            _TransitionsLimit.__loadxml__(element, *args, **kwargs).transitions
#
#        uncertainty = float(element.get('uncertainty'))
#
#        return cls(transitions, uncertainty)
#
#    def __savexml__(self, element, *args, **kwargs):
#        _TransitionsLimit.__savexml__(self, element, *args, **kwargs)
#        element.set('uncertainty', str(self.uncertainty))

#XMLIO.register('{http://pymontecarlo.sf.net}uncertaintyLimit', UncertaintyLimit)
