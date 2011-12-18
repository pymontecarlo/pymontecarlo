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
from pymontecarlo.util.xmlutil import objectxml

# Globals and constants variables.

class Body(objectxml):
    def __init__(self, material):
        """
        Body of a geometry.
        
        :arg material: material of the layer
        :type material: :class:`Material`
        """
        self.material = material

    def __repr__(self):
        return '<Body(material=%s)>' % str(self.material)

    @classmethod
    def __loadxml__(cls, element, material=None, *args, **kwargs):
        if material is None:
            child = list(element.find("material"))[0]
            material = objectxml.from_xml(child)

        return cls(material)

    def __savexml__(self, element, *args, **kwargs):
        child = Element('material')
        child.append(self.material.to_xml())
        element.append(child)

    @property
    def material(self):
        return self._material

    @material.setter
    def material(self, m):
        self._material = m

class Layer(Body):
    def __init__(self, material, thickness):
        """
        Layer of a geometry.
        
        :arg material: material of the layer
        :type material: :class:`Material`
        
        :arg thickness: thickness of the layer in meters
        """
        Body.__init__(self, material)

        self.thickness = thickness

    def __repr__(self):
        return '<Layer(material=%s, thickness=%s m)>' % (str(self.material), self.thickness)

    @classmethod
    def __loadxml__(cls, element, material=None, thickness=None, *args, **kwargs):
        body = Body.__loadxml__(element, material, *args, **kwargs)

        if thickness is None:
            thickness = float(element.get('thickness'))

        return cls(body.material, thickness)

    def __savexml__(self, element, *args, **kwargs):
        Body.__savexml__(self, element, *args, **kwargs)
        element.set('thickness', str(self.thickness))

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

