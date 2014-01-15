#!/usr/bin/env python
"""
================================================================================
:mod:`body` -- Body for geometry
================================================================================

.. module:: body
   :synopsis: Body for geometry

.. inheritance-diagram:: pymontecarlo.input.body

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

__all__ = ['Body',
           'Layer']

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.parameter import \
    ParameterizedMetaClass, Parameter, UnitParameter, SimpleValidator
from pymontecarlo.options.material import Material
from pymontecarlo.options.xmlmapper import \
    (mapper, ParameterizedElement, Attribute, ParameterizedAttribute,
     PythonType, UserType)

# Globals and constants variables.

class Body(object, metaclass=ParameterizedMetaClass):

    material = Parameter(doc="Material of this body")

    def __init__(self, material):
        """
        Body of a geometry.

        :arg material: material of the layer
        :type material: :class:`Material`
        """
        self.material = material

    def __repr__(self):
        return '<Body(material=%s)>' % str(self.material)

mapper.register(Body, '{http://pymontecarlo.sf.net}body',
                ParameterizedElement('material', UserType(Material), optional=True),
                Attribute('_index', PythonType(int), 'index', optional=True))

_thickness_validator = SimpleValidator(lambda t: t > 0,
                                       "Thickness must be greater than 0")

class Layer(Body):

    thickness = UnitParameter("m", _thickness_validator,
                              "Thickness of this layer in meters")

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

mapper.register(Layer, '{http://pymontecarlo.sf.net}layer',
                ParameterizedAttribute('thickness_m', PythonType(float), 'thickness'))
