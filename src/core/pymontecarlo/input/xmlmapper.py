#!/usr/bin/env python
"""
================================================================================
:mod:`xmlmapper` -- XML mapper for inputs
================================================================================

.. module:: xmlmapper
   :synopsis: XML mapper for inputs

.. inheritance-diagram:: pymontecarlo.input.xmlmapper

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlmapper import * #@UnusedWildImport
from pymontecarlo.util.xmlmapper import _XMLType #@UnusedImport
from pymontecarlo.util.mathutil import vector2d, vector3d

# Globals and constants variables.

class ParametrizedAttribute(Attribute):
    
    def __init__(self, objattr, type_, xmlname=None, *args, **kwargs):
        Attribute.__init__(self, objattr, type_, xmlname, True, *args, **kwargs)

    def _get_object_values(self, obj, manager):
        wrapper = obj.__dict__[self.objattr]
        values = wrapper.get_list()
        return map(self.type_.to_xml, values)

class ParametrizedElement(Element):

    def __init__(self, objattr, type_, xmlname=None, *args, **kwargs):
        Element.__init__(self, objattr, type_, xmlname, True, *args, **kwargs)

    def _get_object_values(self, obj, manager):
        wrapper = obj.__dict__[self.objattr]
        values = wrapper.get_list()
        return map(self.type_.to_xml, values)

mapper = XMLMapper()
mapper.register_namespace('mc', 'http://pymontecarlo.sf.net')

# Register classes in pymontecarlo.util
mapper.register(vector3d, "vector3d",
                Attribute('x', PythonType(float)),
                Attribute('y', PythonType(float)),
                Attribute('z', PythonType(float)))

mapper.register(vector2d, "vector2d",
                Attribute('x', PythonType(float)),
                Attribute('y', PythonType(float)))
