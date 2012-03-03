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
from operator import mul

# Third party modules.
from lxml.etree import Element

# Local modules.
from pymontecarlo.input.base.option import Option
from pymontecarlo.util.xmlutil import XMLIO

# Globals and constants variables.

XMLIO.add_namespace('mc', 'http://pymontecarlo.sf.net/input/base')

class PencilBeam(Option):
    def __init__(self, energy_eV, origin_m=(0, 0, 1), direction=(0, 0, -1),
                 aperture_rad=0.0):
        Option.__init__(self)

        self.energy_eV = energy_eV
        self.origin_m = origin_m
        self.direction = direction
        self.aperture_rad = aperture_rad

    def __repr__(self):
        return '<PencilBeam(energy=%s eV, origin=%s m, direction=%s, aperture=%s rad)>' % \
            (self.energy_eV, self.origin_m, self.direction, self.aperture_rad)

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        energy = float(element.get('energy'))

        attrib = element.find('origin').attrib
        origin = map(float, map(attrib.get, ('x', 'y', 'z')))

        attrib = element.find('direction').attrib
        direction = map(float, map(attrib.get, ('x', 'y', 'z')))

        aperture = float(element.get('aperture'))

        return cls(energy, origin, direction, aperture)

    def __savexml__(self, element, *args, **kwargs):
        element.set('energy', str(self.energy_eV))

        attrib = dict(zip(('x', 'y', 'z'), map(str, self.origin_m)))
        element.append(Element('origin', attrib))

        attrib = dict(zip(('x', 'y', 'z'), map(str, self.direction)))
        element.append(Element('direction', attrib))

        element.set('aperture', str(self.aperture_rad))

    @property
    def energy_eV(self):
        """
        Energy of this electron beam (in eV).
        """
        return self._props['energy']

    @energy_eV.setter
    def energy_eV(self, energy):
        if energy <= 0:
            raise ValueError, "Energy (%s) must be greater than 0 eV." % energy
        self._props['energy'] = energy

    @property
    def origin_m(self):
        """
        Starting location of this electron beam.
        Location saved in a tuple of length 3 for the x, y and z coordinates.
        All coordinates are expressed in meters.
        """
        return self._props['origin']

    @origin_m.setter
    def origin_m(self, origin):
        if len(origin) != 3:
            raise ValueError, "Origin must be a tuple of length 3."
        self._props['origin'] = tuple(origin)

    @property
    def direction(self):
        """
        Direction of this electron beam.
        Direction is represented by a tuple of length 3 for the x, y and z 
        coordinates.
        """
        return self._props['direction']

    @direction.setter
    def direction(self, direction):
        if len(direction) != 3:
            raise ValueError, "Direction must be a tuple of length 3."
        self._props['direction'] = tuple(direction)

    @property
    def aperture_rad(self):
        """
        Angular aperture of the electron beam (in radians).
        """
        return self._props['aperture']

    @aperture_rad.setter
    def aperture_rad(self, aperture):
        if aperture < 0.0 or aperture > math.pi / 2:
            raise ValueError, "Aperture (%s) must be between [0, pi/2] rad." % aperture
        self._props['aperture'] = aperture

XMLIO.register('{http://pymontecarlo.sf.net/input/base}pencilBeam', PencilBeam)
XMLIO.register_loader('pymontecarlo.input.base.beam.PencilBeam', PencilBeam)

class GaussianBeam(PencilBeam):
    def __init__(self, energy_eV, diameter_m, origin_m=(0, 0, 1),
                 direction=(0, 0, -1), aperture_rad=0.0):
        PencilBeam.__init__(self, energy_eV, origin_m, direction, aperture_rad)

        self.diameter_m = diameter_m

    def __repr__(self):
        return '<GaussianBeam(energy=%s eV, diameter=%s m, origin=%s m, direction=%s, aperture=%s rad)>' % \
            (self.energy_eV, self.diameter_m, self.origin_m, self.direction, self.aperture_rad)

    @classmethod
    def __loadxml__ (cls, element, *args, **kwargs):
        pencil = PencilBeam.__loadxml__(element, *args, **kwargs)

        diameter_m = float(element.get('diameter'))

        return cls(pencil.energy_eV, diameter_m, pencil.origin_m,
                   pencil.direction, pencil.aperture_rad)

    def __savexml__(self, element, *args, **kwargs):
        PencilBeam.__savexml__(self, element, *args, **kwargs)
        element.set('diameter', str(self.diameter_m))

    @property
    def diameter_m(self):
        """
        Diameter of this electron beam (in meters).
        """
        return self._props['diameter']

    @diameter_m.setter
    def diameter_m(self, diameter):
        if diameter < 0:
            raise ValueError, "Diameter (%s) must be equal or greater than 0." % diameter
        self._props['diameter'] = diameter

XMLIO.register('{http://pymontecarlo.sf.net/input/base}gaussianBeam', GaussianBeam)
XMLIO.register_loader('pymontecarlo.input.base.beam.GaussianBeam', GaussianBeam)

def tilt_beam(angle_rad, axis='y', direction=(0, 0, -1)):
    """
    Returns the direction of the beam after being tilted by an *angle* along
    the specified *axis* of rotation from its original *direction*.
    
    :arg angle_rad: angle of rotation in radians
    :arg axis: axis of rotation, either ``x``, ``y``, ``z``
    :arg direction: original direction of the beam
    
    :return: a 3-length :class:`tuple`
    """
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)

    if axis.lower() == 'x':
        r = [[1, 0, 0], [0, c, -s], [0, s, c]]
    elif axis.lower() == 'y':
        r = [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    elif axis.lower() == 'z':
        r = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    else:
        raise ValueError, "Unknown axis: %s" % axis

    return [sum(map(mul, r[0], direction)),
            sum(map(mul, r[1], direction)),
            sum(map(mul, r[2], direction))]
