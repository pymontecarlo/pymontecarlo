#!/usr/bin/env python
"""
================================================================================
:mod:`beam` -- Parameters of the electron beam
================================================================================

.. module:: beam
   :synopsis: Parameters of the electron beam

.. inheritance-diagram:: beam

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math
from xml.etree.ElementTree import Element

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlobj import XMLObject

# Globals and constants variables.

class PencilBeam(XMLObject):

    def __init__(self, energy, origin=(0, 0, 1), direction=(0, 0, -1),
                 aperture=0.0):
        XMLObject.__init__(self)

        self.energy = energy
        self.origin = origin
        self.direction = direction
        self.aperture = aperture

    def __repr__(self):
        return '<PencilBeam(energy=%s eV, origin=%s m, direction=%s, aperture=%s rad)>' % \
            (self.energy, self.origin, self.direction, self.aperture)

    @classmethod
    def from_xml(cls, element):
        energy = float(element.get("energy"))

        attrib = element.find("origin").attrib
        origin = map(float, map(attrib.get, ('x', 'y', 'z')))

        attrib = element.find("direction").attrib
        direction = map(float, map(attrib.get, ('x', 'y', 'z')))

        aperture = float(element.get("aperture"))

        return cls(energy, origin, direction, aperture)

    @property
    def energy(self):
        """
        Energy of this electron beam (in eV).
        """
        return self._energy

    @energy.setter
    def energy(self, energy):
        if energy <= 0:
            raise ValueError, "Energy (%s) must be greater than 0." % energy
        self._energy = energy

    @property
    def origin(self):
        """
        Starting location of this electron beam.
        Location saved in a tuple of length 3 for the x, y and z coordinates.
        All coordinates are expressed in meters.
        """
        return self._origin

    @origin.setter
    def origin(self, origin):
        if len(origin) != 3:
            raise ValueError, "Origin must be a tuple of length 3."
        self._origin = tuple(origin)

    @property
    def direction(self):
        """
        Direction of this electron beam.
        Direction is represented by a tuple of length 3 for the x, y and z 
        coordinates.
        """
        return self._direction

    @direction.setter
    def direction(self, direction):
        if len(direction) != 3:
            raise ValueError, "Direction must be a tuple of length 3."
        self._direction = tuple(direction)

    @property
    def aperture(self):
        """
        Angular aperture of the electron beam (in radians).
        """
        return self._aperture

    @aperture.setter
    def aperture(self, aperture):
        if aperture < 0.0 or aperture > math.pi / 2:
            raise ValueError, "Aperture (%s) must be between [0, pi/2] rad." % aperture
        self._aperture = aperture

    def to_xml(self):
        element = Element(self.__class__.__name__)

        element.set("energy", str(self.energy))

        attrib = dict(zip(('x', 'y', 'z'), map(str, self.origin)))
        element.append(Element("origin", attrib))

        attrib = dict(zip(('x', 'y', 'z'), map(str, self.direction)))
        element.append(Element("direction", attrib))

        element.set("aperture", str(self.aperture))

        return element

class GaussianBeam(PencilBeam):

    def __init__(self, energy, diameter, origin=(0, 0, 1),
                 direction=(0, 0, 0), aperture=0.0):
        PencilBeam.__init__(self, energy, origin, direction, aperture)

        self.diameter = diameter

    def __repr__(self):
        return '<GaussianBeam(energy=%s eV, diameter=%s m, origin=%s m, direction=%s, aperture=%s rad)>' % \
            (self.energy, self.diameter, self.origin, self.direction, self.aperture)

    @classmethod
    def from_xml(cls, element):
        pencil = PencilBeam.from_xml(element)

        diameter = float(element.get("diameter"))

        return cls(pencil.energy, diameter, pencil.origin,
                   pencil.direction, pencil.aperture)

    @property
    def diameter(self):
        """
        Diameter of this electron beam (in meters).
        """
        return self._diameter

    @diameter.setter
    def diameter(self, diameter):
        if diameter < 0:
            raise ValueError, "Diameter (%s) must be equal or greater than 0." % diameter
        self._diameter = diameter

    def to_xml(self):
        element = PencilBeam.to_xml(self)

        element.set('diameter', str(self.diameter))

        return element

