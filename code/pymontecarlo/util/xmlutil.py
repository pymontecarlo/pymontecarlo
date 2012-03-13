#!/usr/bin/env python
"""
================================================================================
:mod:`xmlutil` -- XML utilities
================================================================================

.. module:: xmlutil
   :synopsis: XML utilities

.. inheritance-diagram:: pymontecarlo.util.xmlutil

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.
from lxml.etree import Element, XMLSchema

# Local modules.

# Globals and constants variables.

class objectxml(object):

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        return cls()

    def __savexml__(self, element, *args, **kwargs):
        pass

    @classmethod
    def from_xml(cls, element, validate=True, *args, **kwargs):
        return XMLIO.from_xml(element, validate, *args, **kwargs)

    def to_xml(self, validate=True, *args, **kwargs):
        return XMLIO.to_xml(self, validate, *args, **kwargs)

class _XMLIO(object):
    def __init__(self):
        self._loaders = {}
        self._savers = {}
        self._nsmap = {}
        self._locations = {}

    def add_namespace(self, prefix, uri, location=None):
        """
        Registers a namespace to be used when loading and saving from/to XML.
        Optionally, the location of the XSD schema file for this namespace
        can be specified.
        
        :arg prefix: prefix of the namespace
        :arg uri: URI of the namespace
        :arg location: location of the XSD schema (optional)
        """
        if prefix in self._nsmap and self._nsmap.get(prefix) != uri:
            raise ValueError, 'A URI (%s) is already associated with this prefix (%s)' % \
                    (self._nsmap[prefix], prefix)

        self._nsmap[prefix] = uri
        if location is not None:
            self._locations[prefix] = os.path.abspath(location)

    def register(self, tag, klass):
        """
        Associates a tag with a class. This class will be used to load every
        element with the specified tag. Every object of this class will be saved
        with the specifed tag.
        
        Raises :exc:`ValueError` if the specified tag is already associated with
        a different class. 
        
        :arg tag: XML tag for the root element
        :arg klass: class extending :class:`objectxml`
        """
        self.register_loader(tag, klass)
        self.register_saver(tag, klass)

    def register_loader(self, tag, klass):
        """
        Associates a tag with a class. This class will be used to load every
        element with the specified tag.
        
        Raises :exc:`ValueError` if the specified tag is already associated with
        a different class. 
        Note that several loaders can be associated with the same class.
        
        :arg tag: XML tag for the root element
        :arg klass: class extending :class:`objectxml`
        """
        if tag in self._loaders and self._loaders.get(tag) != klass:
            raise ValueError, 'A class (%s) is already registered with the tag (%s).' % \
                (self._loaders[tag].__name__, tag)

        if not issubclass(klass, objectxml):
            raise ValueError, 'The class (%s) must be a subclass of objectxml.' % \
                klass.__name__

        self._loaders[tag] = klass

    def register_saver(self, tag, klass):
        """
        Associates a tag with a class. Every object of this class will be saved
        with the specified tag.
        
        Raises :exc:`ValueError` if the specified tag is already associated with
        a different class. 
        Note that a class can only have one tag.
        
        :arg tag: XML tag for the root element
        :arg klass: class extending :class:`objectxml`
        """
        if klass in self._savers and self._savers.get(klass) != tag:
            raise ValueError, 'A tag (%s) is already associated with class (%s).' % \
                (self._savers[klass], klass.__name__)

        if not issubclass(klass, objectxml):
            raise ValueError, 'The class (%s) must be a subclass of objectxml.' % \
                klass.__name__

        self._savers[klass] = tag

    def _create_global_schema(self):
        nsmap_infos = []
        for prefix, uri in self._nsmap.iteritems():
            location = self._locations.get(prefix, '')
            if os.path.exists(location):
                nsmap_infos.append((prefix, uri, location))

        nsmap = {'xsd': 'http://www.w3.org/2001/XMLSchema'}
        for prefix, uri, _filepath in nsmap_infos:
            nsmap[prefix] = uri

        root = Element('{http://www.w3.org/2001/XMLSchema}schema', nsmap=nsmap)

        for _prefix, uri, filepath in nsmap_infos:
            element = Element('{http://www.w3.org/2001/XMLSchema}import')
            element.set('namespace', uri)
            element.set('schemaLocation', filepath)

            root.append(element)

        return XMLSchema(etree=root)

    def validate(self, element):
        schema = self._create_global_schema()
        schema.assertValid(element) # raise exceptions

    def from_xml(self, element, validate=False, *args, **kwargs):
        """
        Loads an object from a XML element. A :exc:`ValueError` is raised if
        no loader is found for the XML element.
        
        :arg element: XML element
        :arg validate: whether to validate element using XSD schema before loading
        """
        if validate:
            self.validate(element)

        tag = element.tag
        if tag not in self._loaders:
            raise ValueError, 'No loader found for element (%s). Please register it first.' % tag
        klass = self._loaders[tag]

        return klass.__loadxml__(element, *args, **kwargs)

    def to_xml(self, obj, validate=False, *args, **kwargs):
        """
        Saves an object as a XML element. A :exc:`ValueError` is raised if
        no saver is found for the object.
        
        :arg obj: object
        :arg validate: whether to validate element using XSD schema before 
            returning the XML element
        """
        klass = obj.__class__
        if klass not in self._savers:
            raise ValueError, 'No saver found for class (%s). Please register it first.' % klass

        tag = self._savers[klass]
        element = Element(tag, nsmap=self._nsmap)

        obj.__savexml__(element, *args, **kwargs)

        if validate:
            self.validate(element)

        return element

XMLIO = _XMLIO()

