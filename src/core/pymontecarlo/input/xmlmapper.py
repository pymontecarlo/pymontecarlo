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
from pyxray.transition import Transition

# Local modules.
from pymontecarlo.util.xmlmapper import * #@UnusedWildImport
from pymontecarlo.util.xmlmapper import _XMLType, _XMLItem #@UnusedImport
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
                 keyxmlname='{xmlmapper}key', valuexmlname='{xmlmapper}value',
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

    def _set_object_values(self, obj, values):
        keys = map(itemgetter(0), values)
        keys = map(self.keytype.from_xml, keys)

        values = map(itemgetter(1), values)
        values = map(self.type_.from_xml, values)

        if not values and self.optional:
            return

        d = getattr(obj, self.objattr)
        d.clear()
        d.update(dict(zip(keys, values)))

class ParameterizedElementSet(Element):

    def __init__(self, objattr, type_, xmlname=None, optional=False,
                 *args, **kwargs):
        Element.__init__(self, objattr, type_, xmlname, True, optional,
                         *args, **kwargs)

    def _get_object_values(self, obj, manager):
        try:
            wrapper = obj.__dict__[self.objattr]
        except AttributeError:
            if self.optional:
                return []
            else:
                raise

        values = wrapper.get()
        values = map(self.type_.to_xml, values)
        return values

    def _set_object_values(self, obj, values):
        values = map(self.type_.from_xml, values)

        if not values and self.optional:
            return

        s = getattr(obj, self.objattr)
        s.clear()
        s |= set(values)

class ParameterizedElementSequence(Element):

    def __init__(self, objattr, type_, xmlname=None, optional=False,
                 *args, **kwargs):
        Element.__init__(self, objattr, type_, xmlname, True, optional,
                         *args, **kwargs)

    def _get_object_values(self, obj, manager):
        try:
            wrapper = obj.__dict__[self.objattr]
        except AttributeError:
            if self.optional:
                return []
            else:
                raise

        values = wrapper.get()
        values = map(self.type_.to_xml, values)
        return values

    def _set_object_values(self, obj, values):
        values = map(self.type_.from_xml, values)

        if not values and self.optional:
            return

        s = getattr(obj, self.objattr)
        del s[:]
        s.extend(values)

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

class _SubshellType(_XMLType):

    def to_xml(self, value):
        return str(value.index)
    
    def from_xml(self, value):
        return int(value)

mapper.register(Transition, 'transition',
                Attribute('_z', PythonType(int), 'z'),
                Attribute('_src', _SubshellType(), 'src'),
                Attribute('_dest', _SubshellType(), 'dest'),
                Attribute('_satellite', PythonType(int), 'satellite', optional=True))
