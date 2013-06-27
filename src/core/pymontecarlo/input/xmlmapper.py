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

class ParameterizedAttribute(Attribute):
    
    def __init__(self, objattr, type_, xmlname=None, *args, **kwargs):
        Attribute.__init__(self, objattr, type_, xmlname, True, *args, **kwargs)

    def _get_object_values(self, obj, manager):
        try:
            wrapper = obj.__dict__[self.objattr]
        except AttributeError:
            if self.optional:
                return []
            else:
                raise
        
        values = wrapper.get_list()
        return map(self.type_.to_xml, values)

class ParameterizedElement(Element):

    def __init__(self, objattr, type_, xmlname=None, *args, **kwargs):
        Element.__init__(self, objattr, type_, xmlname, True, *args, **kwargs)

    def _get_object_values(self, obj, manager):
        try:
            wrapper = obj.__dict__[self.objattr]
        except AttributeError:
            if self.optional:
                return []
            else:
                raise

        values = wrapper.get_list()
        return map(self.type_.to_xml, values)

class ParameterizedElementDict(ElementDict):

    def __init__(self, objattr, keytype, valuetype, xmlname=None,
                 keyxmlname='_key', valuexmlname='value',
                 optional=False, *args, **kwargs):
        ElementDict.__init__(self, objattr, keytype, valuetype, xmlname,
                             keyxmlname, valuexmlname, optional, *args, **kwargs)

    def _get_object_values(self, obj, manager):
        try:
            wrapper = obj.__dict__[self.objattr]
        except AttributeError:
            if self.optional:
                return []
            else:
                raise

        d = wrapper.get()

        keys = d.keys()
        keys = map(self.keytype.to_xml, keys)

        values = d.values()
        values = map(self.type_.to_xml, values)

        return zip(keys, values)

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
