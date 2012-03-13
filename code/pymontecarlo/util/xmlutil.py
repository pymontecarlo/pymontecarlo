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
from pymontecarlo.util.manager import Manager

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

class _XMLIO(Manager):
    def __init__(self):
        Manager.__init__(self)

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

    def register_loader(self, tag, klass):
        if not issubclass(klass, objectxml):
            raise ValueError, 'The class (%s) must be a subclass of objectxml.' % \
                klass.__name__

        Manager.register_loader(self, tag, klass)

    def register_saver(self, tag, klass):
        if not issubclass(klass, objectxml):
            raise ValueError, 'The class (%s) must be a subclass of objectxml.' % \
                klass.__name__

        Manager.register_saver(self, tag, klass)

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

        klass = self._get_class(element.tag)

        return klass.__loadxml__(element, *args, **kwargs)

    def to_xml(self, obj, validate=False, *args, **kwargs):
        """
        Saves an object as a XML element. A :exc:`ValueError` is raised if
        no saver is found for the object.
        
        :arg obj: object
        :arg validate: whether to validate element using XSD schema before 
            returning the XML element
        """
        tag = self._get_tag(obj.__class__)
        element = Element(tag, nsmap=self._nsmap)

        obj.__savexml__(element, *args, **kwargs)

        if validate:
            self.validate(element)

        return element

XMLIO = _XMLIO()

