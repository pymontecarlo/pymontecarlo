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

# Standard library modules.
from xml.etree.ElementTree import Element

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlutil import objectxml
from pymontecarlo.util.transition import Transition

# Globals and constants variables.

class _TransitionLimit(objectxml):
    def __init__(self, transition):
        self.transition = transition

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        child = list(element.find("transition"))[0]
        transition = Transition.__loadxml__(child, *args, **kwargs)

        return cls(transition)

    def __savexml__(self, element, *args, **kwargs):
        child = Element('transition')
        child.append(self.transition.to_xml())
        element.append(child)

    @property
    def transition(self):
        return self._transition

    @transition.setter
    def transition(self, transition):
        self._transition = transition

class TimeLimit(objectxml):
    def __init__(self, time):
        self.time = time

    def __repr__(self):
        return '<TimeLimit(time=%s s)>' % self.time

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        time = long(element.get('time'))
        return cls(time)

    def __savexml__(self, element, *args, **kwargs):
        element.set('time', str(self.time))

    @property
    def time(self):
        """
        Simulation time in seconds.
        """
        return self._time

    @time.setter
    def time(self, time):
        if time <= 0:
            raise ValueError, "Time (%s) must be greater than 0." % time
        self._time = long(time)

class ShowersLimit(objectxml):
    def __init__(self, showers):
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
        return self._showers

    @showers.setter
    def showers(self, showers):
        if showers < 1:
            raise ValueError, "Number of showers (%s) must be equal or greater than 1." % showers
        self._showers = long(showers)

class UncertaintyLimit(_TransitionLimit):
    def __init__(self, transition, uncertainty):
        _TransitionLimit.__init__(self, transition)

        self.uncertainty = uncertainty

    def __repr__(self):
        return '<UncertaintyLimit(transition=%s, uncertainty=%s %%)>' % \
            (str(self.transition), self.uncertainty * 100.0)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        transition = _TransitionLimit.__loadxml__(element, *args, **kwargs).transition

        uncertainty = float(element.get('uncertainty'))

        return cls(transition, uncertainty)

    def __savexml__(self, element, *args, **kwargs):
        _TransitionLimit.__savexml__(self, element, *args, **kwargs)
        element.set('uncertainty', str(self.uncertainty))

    @property
    def uncertainty(self):
        return self._uncertainty

    @uncertainty.setter
    def uncertainty(self, unc):
        if unc < 0 or unc > 1:
            raise ValueError, "Relative uncertainty (%s) must be between [0.0, 1.0]." % unc
        self._uncertainty = unc
