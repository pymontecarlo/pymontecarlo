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
from pymontecarlo.util.xmlobj import XMLObject
from pymontecarlo.util.transition import Transition

# Globals and constants variables.

class _TransitionLimit(XMLObject):
    def __init__(self, transition):
        XMLObject.__init__(self)

        self.transition = transition

    @classmethod
    def from_xml(cls, element):
        child = list(element.find("transition"))[0]
        material = Transition.from_xml(child)

        return cls(material)

    @property
    def transition(self):
        return self._transition

    @transition.setter
    def transition(self, transition):
        self._transition = transition

    def to_xml(self):
        element = XMLObject.to_xml(self)

        child = Element('transition')
        child.append(self.transition.to_xml())
        element.append(child)

        return element

class TimeLimit(XMLObject):
    def __init__(self, time):
        XMLObject.__init__(self)

        self.time = time

    def __repr__(self):
        return '<TimeLimit(time=%s s)>' % self.time

    @classmethod
    def from_xml(cls, element):
        time = long(element.get('time'))
        return cls(time)

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

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.set('time', str(self.time))

        return element

class ShowersLimit(XMLObject):
    def __init__(self, showers):
        XMLObject.__init__(self)

        self.showers = showers

    @classmethod
    def from_xml(cls, element):
        showers = long(element.get('showers'))
        return cls(showers)

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

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.set('showers', str(self.showers))

        return element

class UncertaintyLimit(_TransitionLimit):
    def __init__(self, transition, uncertainty):
        _TransitionLimit.__init__(self, transition)

        self.uncertainty = uncertainty

    def __repr__(self):
        return '<UncertaintyLimit(transition=%s, uncertainty=%s %%)>' % \
            (str(self.transition), self.uncertainty * 100.0)

    @classmethod
    def from_xml(cls, element):
        transition = _TransitionLimit.from_xml(element).transition

        uncertainty = float(element.get('uncertainty'))

        return cls(transition, uncertainty)

    @property
    def uncertainty(self):
        return self._uncertainty

    @uncertainty.setter
    def uncertainty(self, unc):
        if unc < 0 or unc > 1:
            raise ValueError, "Relative uncertainty (%s) must be between [0.0, 1.0]." % unc
        self._uncertainty = unc

    def to_xml(self):
        element = _TransitionLimit.to_xml(self)

        element.set('uncertainty', str(self.uncertainty))

        return element
