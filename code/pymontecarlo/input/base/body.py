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

# Third party modules.
from lxml.etree import Element

# Local modules.
from pymontecarlo.input.base.option import Option
from pymontecarlo.util.xmlutil import XMLIO

# Globals and constants variables.

class Body(Option):
    def __init__(self, material):
        """
        Body of a geometry.
        
        :arg material: material of the layer
        :type material: :class:`Material`
        """
        Option.__init__(self)

        self.material = material

    def __repr__(self):
        return '<Body(material=%s)>' % str(self.material)

    @classmethod
    def __loadxml__(cls, element, material=None, *args, **kwargs):
        if material is None:
            child = list(element.find('material'))[0]
            material = XMLIO.from_xml(child)

        return cls(material)

    def __savexml__(self, element, *args, **kwargs):
        child = element.find('material')
        if child is not None:
            child.clear()
            child.append(self.material.to_xml())
        else:
            child = Element('material')
            child.append(self.material.to_xml())
            element.append(child)

    @property
    def material(self):
        return self._props['material']

    @material.setter
    def material(self, m):
        self._props['material'] = m

XMLIO.register('{http://pymontecarlo.sf.net/input/base}body', Body)
XMLIO.register_loader('pymontecarlo.input.base.body.Body', Body)

class Layer(Body):
    def __init__(self, material, thickness_m):
        """
        Layer of a geometry.
        
        :arg material: material of the layer
        :type material: :class:`Material`
        
        :arg thickness_m: thickness of the layer in meters
        """
        Body.__init__(self, material)

        self.thickness_m = thickness_m

    def __repr__(self):
        return '<Layer(material=%s, thickness=%s m)>' % \
                    (str(self.material), self.thickness_m)

    @classmethod
    def __loadxml__(cls, element, material=None, thickness_m=None, *args, **kwargs):
        body = Body.__loadxml__(element, material, *args, **kwargs)

        if thickness_m is None:
            thickness_m = float(element.get('thickness'))

        return cls(body.material, thickness_m)

    def __savexml__(self, element, *args, **kwargs):
        Body.__savexml__(self, element, *args, **kwargs)
        element.set('thickness', str(self.thickness_m))

    @property
    def thickness_m(self):
        """
        Thickness of this layer in meters.
        """
        return self._props['thickness']

    @thickness_m.setter
    def thickness_m(self, thickness):
        if thickness <= 0:
            raise ValueError, "Thickness (%s) must be greater than 0." % thickness
        self._props['thickness'] = thickness

XMLIO.register('{http://pymontecarlo.sf.net/input/base}layer', Layer)
XMLIO.register_loader('pymontecarlo.input.base.body.Layer', Layer)
