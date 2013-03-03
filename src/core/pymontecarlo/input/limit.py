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
from pymontecarlo.input.option import Option
from pymontecarlo.util.xmlutil import XMLIO

# Globals and constants variables.

class _TransitionsLimit(Option):
    def __init__(self, transitions):
        Option.__init__(self)

        self._props['transitions'] = set()

        if hasattr(transitions, '__iter__'):
            self.transitions.update(transitions)
        else:
            self.transitions.add(transitions)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        transitions = set()
        for child in list(element):
            transitions.add(XMLIO.from_xml(child, *args, **kwargs))

        return cls(transitions)

    def __savexml__(self, element, *args, **kwargs):
        for transition in self.transitions:
            element.append(transition.to_xml())

    @property
    def transitions(self):
        """
        Transitions for the limit.
        
        :rtype: :class:`list`
        """
        return self._props['transitions']

class TimeLimit(Option):
    def __init__(self, time):
        Option.__init__(self)

        self.time_s = time

    def __repr__(self):
        return '<TimeLimit(time=%s s)>' % self.time_s

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        time = long(element.get('time'))
        return cls(time)

    def __savexml__(self, element, *args, **kwargs):
        element.set('time', str(self.time_s))

    @property
    def time_s(self):
        """
        Simulation time in seconds.
        """
        return self._props['time']

    @time_s.setter
    def time_s(self, time):
        if time <= 0:
            raise ValueError, "Time (%s) must be greater than 0." % time
        self._props['time'] = long(time)

XMLIO.register('{http://pymontecarlo.sf.net}timeLimit', TimeLimit)

class ShowersLimit(Option):
    def __init__(self, showers):
        Option.__init__(self)

        self.showers = showers

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        showers = long(element.get('showers'))
        return cls(showers)

    def __savexml__(self, element, *args, **kwargs):
        element.set('showers', str(self.showers))

    def __repr__(self):
        return '<ShowersLimit(showers=%s)>' % self.showers

    @property
    def showers(self):
        """
        Number of electron showers.
        """
        return self._props['showers']

    @showers.setter
    def showers(self, showers):
        if showers < 1:
            raise ValueError, "Number of showers (%s) must be equal or greater than 1." % showers
        self._props['showers'] = long(showers)

XMLIO.register('{http://pymontecarlo.sf.net}showersLimit', ShowersLimit)

class UncertaintyLimit(_TransitionsLimit):
    def __init__(self, transitions, uncertainty):
        _TransitionsLimit.__init__(self, transitions)

        self.uncertainty = uncertainty

    def __repr__(self):
        return '<UncertaintyLimit(%i transitions, uncertainty=%s %%)>' % \
            (len(self.transitions), self.uncertainty * 100.0)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        transitions = \
            _TransitionsLimit.__loadxml__(element, *args, **kwargs).transitions

        uncertainty = float(element.get('uncertainty'))

        return cls(transitions, uncertainty)

    def __savexml__(self, element, *args, **kwargs):
        _TransitionsLimit.__savexml__(self, element, *args, **kwargs)
        element.set('uncertainty', str(self.uncertainty))

    @property
    def uncertainty(self):
        return self._props['uncertainty']

    @uncertainty.setter
    def uncertainty(self, unc):
        if unc < 0 or unc > 1:
            raise ValueError, "Relative uncertainty (%s) must be between [0.0, 1.0]." % unc
        self._props['uncertainty'] = unc

XMLIO.register('{http://pymontecarlo.sf.net}uncertaintyLimit', UncertaintyLimit)
