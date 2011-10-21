#!/usr/bin/env python
"""
================================================================================
:mod:`body` -- Body for geometry
================================================================================

.. module:: body
   :synopsis: Body for geometry

.. inheritance-diagram:: body

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
from pymontecarlo.input.material import Material

# Globals and constants variables.

class Body(XMLObject):
    def __init__(self, material):
        XMLObject.__init__(self)

        self.material = material

    def __repr__(self):
        return '<Body(material=%s)>' % str(self.material)

    @classmethod
    def from_xml(cls, element):
        child = list(element.find("material"))[0]
        material = Material.from_xml(child)

        return cls(material)

    @property
    def material(self):
        return self._material

    @material.setter
    def material(self, m):
        self._material = m

    def to_xml(self):
        element = XMLObject.to_xml(self)

        child = Element('material')
        child.append(self.material.to_xml())
        element.append(child)

        return element

class Layer(Body):
    def __init__(self, material, thickness):
        Body.__init__(self, material)

        self.thickness = thickness

    def __repr__(self):
        return '<Layer(material=%s, thickness=%s m)>' % (str(self.material), self.thickness)

    @classmethod
    def from_xml(cls, element):
        body = Body.from_xml(element)

        thickness = float(element.get('thickness'))

        return cls(body.material, thickness)

    @property
    def thickness(self):
        """
        Thickness of this layer in meters.
        """
        return self._thickness

    @thickness.setter
    def thickness(self, thickness):
        if thickness <= 0:
            raise ValueError, "Thickness (%s) must be greater than 0." % thickness
        self._thickness = thickness

    def to_xml(self):
        element = Body.to_xml(self)

        element.set('thickness', str(self.thickness))

        return element
