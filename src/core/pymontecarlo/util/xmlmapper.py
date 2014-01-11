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
import xml.dom.minidom as minidom
from collections import Iterable
from operator import itemgetter, attrgetter

# Third party modules.

# Local modules.

from pymontecarlo.util.manager import Manager

# Globals and constants variables.
NSPREFIX = 'mapper'
NSURI = 'xmlmapper'

def parse(source):
    return ElementTree.parse(source)

def tostring(element, encoding='UTF-8', pretty_print=True):
    output = ElementTree.tostring(element, encoding=encoding)
    if pretty_print:
        output = minidom.parseString(output).toprettyxml(encoding=encoding)
    return output

class _XMLType(object):

    def from_xml(self, value):
        raise NotImplementedError

    def to_xml(self, value):
        raise NotImplementedError

class PythonType(_XMLType):

    def __init__(self, type_):
        self._type = type_

    def from_xml(self, value):
        # None
        if value == 'xsi:nil':
            return None

        # Boolean
        if self._type is bool:
            if value == 'true':
                return True
            elif value == 'false':
                return False
            else:
                raise ValueError, 'Incorrect boolean value: %s' % value

        return self._type(value)

    def to_xml(self, value):
        # None
        if value is None:
            return 'xsi:nil'

        # Boolean
        if self._type is bool:
            return 'true' if value else 'false'

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

    def __init__(self, objattr, type_, xmlname=None,
                 iterable=False, optional=False, *args, **kwargs):
        self.objattr = objattr
        self.type_ = type_
        self.xmlname = xmlname or objattr
        self.iterable = iterable
        self.optional = optional

    def __repr__(self):
        return '<%s(%s <-> %s)>' % (self.__class__.__name__,
                                    self.objattr, self.xmlname)

    def _get_object_values(self, obj, manager):
        try:
            values = attrgetter(self.objattr)(obj)
        except AttributeError:
            if self.optional:
                return []
            else:
                raise

        if not self.iterable:
            values = [values]
        else:
            if not isinstance(values, Iterable) or \
                    manager.is_registered(klass=values.__class__):
                values = [values]

        return map(self.type_.to_xml, values)

    def _update_element(self, element, values, manager, cache):
        raise NotImplementedError

    def dump(self, obj, element, manager, cache):
        values = self._get_object_values(obj, manager)
        self._update_element(element, values, manager, cache)

    def _extract_values(self, element, manager, cache):
        raise NotImplementedError

    def _set_object_values(self, obj, values):
        values = map(self.type_.from_xml, values)

        if not values and self.optional:
            return

        if not self.iterable:
            values = values[0]

        dots = self.objattr.rsplit('.', 1)
        lastobj = attrgetter(dots[0])(obj) if len(dots) > 1 else obj
        setattr(lastobj, dots[-1], values)

    def load(self, obj, element, manager, cache):
        values = self._extract_values(element, manager, cache)
        self._set_object_values(obj, values)

class Element(_XMLItem):

    def _update_element(self, element, values, manager, cache):
        subelement = ElementTree.Element(self.xmlname)

        if isinstance(self.type_, UserType):
            self._update_element_usertype(subelement, values, manager, cache)
        else:
            self._update_element_nousertype(subelement, values, manager, cache)

        element.append(subelement)

    def _update_element_usertype(self, subelement, values, manager, cache):
        for value in values:
            id_value = id(value)
            if id_value in cache:
                subsubelement = ElementTree.Element('{%s}cache' % NSURI)
                subsubelement.set('{%s}id' % NSURI, str(id_value))
            else:
                subsubelement = manager.to_xml(value)
                subsubelement.set('{%s}id' % NSURI, str(id_value))
                cache[id_value] = value

            subelement.append(subsubelement)

    def _update_element_nousertype(self, subelement, values, manager, cache):
        text = []
        for value in values:
            if ',' in str(value):
                raise ValueError, "Value %s contains ','. Cannot be serialised" % value
            text.append(value)
        subelement.text = ','.join(text)

    def _extract_values(self, element, manager, cache):
        subelement = element.find(self.xmlname)
        if subelement is None:
            return []

        if isinstance(self.type_, UserType):
            values = self._extract_values_usertype(subelement, manager, cache)
        else:
            values = self._extract_values_nousertype(subelement, manager, cache)

        return values

    def _extract_values_usertype(self, subelement, manager, cache):
        values = []
        for subsubelement in subelement:
            id_value = int(subsubelement.get('{%s}id' % NSURI))
            if subsubelement.tag == '{%s}cache' % NSURI:
                value = cache[id_value]
            else:
                value = manager.from_xml(subsubelement)
                cache[id_value] = value
            values.append(value)
        return values

    def _extract_values_nousertype(self, subelement, manager, cache):
        if not subelement.text:
            return []
        return subelement.text.split(',')

class ElementDict(Element):

    def __init__(self, objattr, keytype, valuetype, xmlname=None,
                 keyxmlname='{%s}key' % NSURI,
                 valuexmlname='{%s}value' % NSURI,
                 optional=False, *args, **kwargs):
        Element.__init__(self, objattr, valuetype, xmlname,
                         iterable=True, optional=optional, *args, **kwargs)
        self.keytype = keytype
        self.keyxmlname = keyxmlname
        self.valuexmlname = valuexmlname

    def _get_object_values(self, obj, manager):
        try:
            d = getattr(obj, self.objattr)
        except AttributeError:
            if self.optional:
                return []
            else:
                raise

        keys = d.keys()
        keys = map(self.keytype.to_xml, keys)

        values = d.values()
        values = map(self.type_.to_xml, values)

        return zip(keys, values)

    def _update_element_usertype(self, subelement, values, manager, cache):
        for key, value in values:
            id_value = id(value)
            if id_value in cache:
                subsubelement = ElementTree.Element('{%s}cache' % NSURI)
                subsubelement.set('{%s}id' % NSURI, str(id_value))
            else:
                subsubelement = manager.to_xml(value)
                subsubelement.set('{%s}id' % NSURI, str(id_value))
                cache[id_value] = value

            subsubelement.set(self.keyxmlname, key)
            subelement.append(subsubelement)

    def _update_element_nousertype(self, subelement, values, manager, cache):
        for key, value in values:
            subsubelement = ElementTree.Element(self.valuexmlname)
            subsubelement.set(self.keyxmlname, key)
            subsubelement.text = value
            subelement.append(subsubelement)

    def _set_object_values(self, obj, values):
        keys = map(itemgetter(0), values)
        keys = map(self.keytype.from_xml, keys)

        values = map(itemgetter(1), values)
        values = map(self.type_.from_xml, values)

        if not values and self.optional:
            return

        setattr(obj, self.objattr, dict(zip(keys, values)))

    def _extract_values_usertype(self, subelement, manager, cache):
        values = []
        for subsubelement in subelement:
            id_value = int(subsubelement.get('{%s}id' % NSURI))
            if subsubelement.tag == '{%s}cache' % NSURI:
                value = cache[id_value]
            else:
                value = manager.from_xml(subsubelement)
                cache[id_value] = value

            key = subsubelement.get(self.keyxmlname)
            values.append((key, value))
        return values

    def _extract_values_nousertype(self, subelement, manager, cache):
        values = []
        for subsubelement in subelement:
            key = subsubelement.get(self.keyxmlname)
            value = subsubelement.text
            values.append((key, value))
        return values

class Attribute(_XMLItem):

    def _update_element(self, element, values, manager, cache):
        if not values:
            return

        text = []
        for value in values:
            if ',' in str(value):
                raise ValueError, "Value %s contains ','. Cannot be serialised" % value
            text.append(value)
        text = ','.join(text)

        element.set(self.xmlname, text)

    def _extract_values(self, element, manager, cache):
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
        self.register_namespace(NSPREFIX, NSURI)

    def register_namespace(self, prefix, uri):
        """
        Registers a namespace to be used when loading and saving from/to XML.

        :arg prefix: prefix of the namespace
        :arg uri: URI of the namespace
        """
        ElementTree.register_namespace(prefix, uri)

    def register(self, klass, tag, *content, **kwargs):
        self._manager.register(tag, klass)

        # Search for the content already registered classes
        if kwargs.get('inherit', True):
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
        except TypeError: # old class style
            recast = True
            obj = _EmptyClass()

        # Load XML
        cache = {}

        for item in content:
            item.load(obj, element, self, cache)

        if recast:
            obj = klass(**obj.__dict__)

        # Reduce
        if hasattr(obj, '__reduce__'):
            rdc = obj.__reduce__()

            func = rdc[0]
            args = rdc[1]
            obj = func(*args)

            # State
            if len(rdc) > 2:
                state = rdc[2]
                if hasattr(obj, '__setstate__'):
                    obj.__setstate__(state)
                else:
                    obj.__dict__.update(state)

            # List items
            if len(rdc) > 3:
                obj.extend(rdc[3])

            # Dict items
            if len(rdc) > 4:
                obj.update(rdc[4])

        return obj

    def to_xml(self, obj):
        """
        Saves an object as a XML element. A :exc:`ValueError` is raised if
        no saver is found for the object.

        :arg obj: object
        """
        tag = self._manager.get_tag(obj.__class__)
        content = self._content[tag]
        cache = {}

        element = ElementTree.Element(tag)

        for item in content:
            item.dump(obj, element, self, cache)

        return element

