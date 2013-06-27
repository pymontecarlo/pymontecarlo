#!/usr/bin/env python
"""
================================================================================
:mod:`xmlmapper` -- Mapper functions to XML
================================================================================

.. module:: xmlmapper
   :synopsis: Mapper functions to XML

.. inheritance-diagram:: pymontecarlo.util.xmlmapper

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import xml.etree.ElementTree as ElementTree
from collections import Iterable

# Third party modules.

# Local modules.

from pymontecarlo.util.manager import Manager

# Globals and constants variables.

class _XMLType(object):

    def from_xml(self, value):
        raise NotImplementedError

    def to_xml(self, value):
        raise NotImplementedError

class PythonType(_XMLType):
    
    def __init__(self, type_):
        self._type = type_

    def from_xml(self, value):
        return self._type(value)

    def to_xml(self, value):
        return str(value)
    
class UserType(_XMLType):
    
    def __init__(self, klass):
        self._klass = klass
        
    def from_xml(self, value):
        assert isinstance(value, self._klass)
        return value
    
    def to_xml(self, value):
        assert isinstance(value, self._klass), \
            '%s != %s' % (value.__class__, self._klass)
        return value

class _XMLItem(object):
    
    def __init__(self, objattr, type_, xmlname=None, iterable=False, *args, **kwargs):
        self.objattr = objattr
        self.type_ = type_
        self.xmlname = xmlname or objattr
        self.iterable = iterable

    def __repr__(self):
        return '<%s(%s <-> %s)>' % (self.__class__.__name__,
                                    self.objattr, self.xmlname)
        
    def _get_object_values(self, obj, manager):
        values = getattr(obj, self.objattr)

        if not self.iterable:
            values = [values]
        else:
            if not isinstance(values, Iterable) or \
                    manager.is_registered(klass=values.__class__):
                values = [values]

        return map(self.type_.to_xml, values)
    
    def _update_element(self, element, values, manager):
        raise NotImplementedError

    def dump(self, obj, element, manager):
        values = self._get_object_values(obj, manager)
        self._update_element(element, values, manager)
        
    def _extract_values(self, element, manager):
        raise NotImplementedError
        
    def _set_object_values(self, obj, values):
        values = map(self.type_.from_xml, values)

        if not self.iterable:
            values = values[0]

        setattr(obj, self.objattr, values)

    def load(self, obj, element, manager):
        values = self._extract_values(element, manager)
        self._set_object_values(obj, values)

class Element(_XMLItem):
    
    def _update_element(self, element, values, manager):
        subelement = ElementTree.Element(self.xmlname)

        if isinstance(self.type_, UserType):
            self._update_element_usertype(subelement, values, manager)
        else:
            self._update_element_nousertype(subelement, values, manager)

        element.append(subelement)
        
    def _update_element_usertype(self, subelement, values, manager):
        for value in values:
            subelement.append(manager.to_xml(value))

    def _update_element_nousertype(self, subelement, values, manager):
        text = []
        for value in values:
            if ',' in str(value):
                raise ValueError, "Value %s contains ','. Cannot be serialised" % value
            text.append(value)
        subelement.text = ','.join(text)

    def _extract_values(self, element, manager):
        subelement = element.find(self.xmlname)
        if subelement is None:
            return []

        subsubelements = list(subelement)
        if subsubelements:
            values = self._extract_values_usertype(subelement, manager)
        else:
            values = self._extract_values_nousertype(subelement, manager)

        return values
    
    def _extract_values_usertype(self, subelement, manager):
        values = []
        for subsubelement in subelement:
            values.append(manager.from_xml(subsubelement))
        return values
    
    def _extract_values_nousertype(self, subelement, manager):
        return subelement.text.split(',')

class Attribute(_XMLItem):

    def _update_element(self, element, values, manager):
        if not values:
            return

        text = []
        for value in values:
            if ',' in str(value):
                raise ValueError, "Value %s contains ','. Cannot be serialised" % value
            text.append(value)
        text = ','.join(text)

        element.set(self.xmlname, text)

    def _extract_values(self, element, manager):
        text = element.get(self.xmlname)
        if text is None:
            return []
        return text.split(',')

class _EmptyClass(object):
    pass

class XMLMapper(object):
    
    def __init__(self):
        self._manager = Manager()
        self._content = {}

    def register_namespace(self, prefix, uri):
        """
        Registers a namespace to be used when loading and saving from/to XML.
        
        :arg prefix: prefix of the namespace
        :arg uri: URI of the namespace
        """
        ElementTree.register_namespace(prefix, uri)

    def register(self, klass, tag, *content):
        self._manager.register(tag, klass)
        
        # Search for the content already registered classes
        for base in klass.__bases__:
            try:
                basetag = self._manager.get_tag(base)
            except ValueError:
                continue
            content += self._content[basetag]
        
        self._content[tag] = content

    def is_registered(self, klass=None, tag=None):
        return self._manager.is_registered(tag, klass)

    def from_xml(self, element):
        """
        Loads an object from a XML element. A :exc:`ValueError` is raised if
        no loader is found for the XML element.
        
        :arg element: XML element
        """
        klass = self._manager.get_class(element.tag)
        content = self._content[element.tag]

        recast = False
        try:
            obj = klass.__new__(klass)
        except TypeError:
            recast = True
            obj = _EmptyClass()

        for item in content:
            item.load(obj, element, self)

        if recast:
            obj = klass(**obj.__dict__)

        return obj

    def to_xml(self, obj):
        """
        Saves an object as a XML element. A :exc:`ValueError` is raised if
        no saver is found for the object.
        
        :arg obj: object
        """
        tag = self._manager.get_tag(obj.__class__)
        content = self._content[tag]

        element = ElementTree.Element(tag)

        for item in content:
            item.dump(obj, element, self)

        return element

