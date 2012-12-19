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

# Third party modules.
from lxml.etree import Element, XMLSchema, tostring, parse

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

    @classmethod
    def load(cls, source, validate=True):
        """
        Loads the object from a file-object.
        The file-object must correspond to a XML file where the options were 
        saved.
        
        :arg source: filepath or file-object
        :arg validate: whether to validate XML file against the schemas 
            (default: ``True``)
        
        :return: loaded object
        """
        self_opened = False
        if not hasattr(source, "read"):
            source = open(source, "rb")
            self_opened = True

        element = parse(source).getroot()
        if self_opened: source.close()

        return cls.from_xml(element, validate)

    def save(self, source, validate=True, pretty_print=True):
        """
        Saves this object to a file-object.
        The file-object must correspond to a XML file where the options will 
        be saved.
        
        :arg source: filepath or file-object
        :arg validate: whether to validate XML file against the schemas 
            (default: ``True``)
        """
        element = self.to_xml(validate)
        output = tostring(element, pretty_print=pretty_print,
                          encoding="UTF-8", xml_declaration=True)

        self_opened = False
        if not hasattr(source, "write"):
            source = open(source, "wb")
            self_opened = True

        source.write(output)

        if self_opened: source.close()

class _XMLIO(Manager):
    def __init__(self):
        Manager.__init__(self)

        self._nsmap = {}
        self._schemas = {}

    def reset(self):
        """
        Unregisters all loaders, savers and namespaces
        """
        Manager.reset(self)
        self._nsmap.clear()
        self._schemas.clear()

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
            self._schemas[prefix] = XMLSchema(file=location)

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

    def validate(self, element):
        exceptions = []

        for prefix in getattr(element, 'nsmap', []):
            schema = self._schemas.get(prefix)
            if schema is None:
                continue

            try:
                schema.assertValid(element)
            except Exception as ex:
                exceptions.append(ex)
                continue

            return

        if exceptions:
            if len(exceptions) == 1:
                raise exceptions[0]
            else:
                raise Exception, '; '.join(map(str, exceptions))

    def from_xml(self, element, validate=False, *args, **kwargs):
        """
        Loads an object from a XML element. A :exc:`ValueError` is raised if
        no loader is found for the XML element.
        
        :arg element: XML element
        :arg validate: whether to validate element using XSD schema before loading
        """
        if validate:
            self.validate(element)

        klass = self.get_class(element.tag)

        return klass.__loadxml__(element, *args, **kwargs)

    def to_xml(self, obj, validate=False, *args, **kwargs):
        """
        Saves an object as a XML element. A :exc:`ValueError` is raised if
        no saver is found for the object.
        
        :arg obj: object
        :arg validate: whether to validate element using XSD schema before 
            returning the XML element
        """
        tag = self.get_tag(obj.__class__)
        element = Element(tag, nsmap=self._nsmap)

        obj.__savexml__(element, *args, **kwargs)

        if validate:
            self.validate(element)

        return element

XMLIO = _XMLIO()

