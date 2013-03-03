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
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
import xml.dom.minidom as minidom

# Local modules.
from pymontecarlo.util.manager import Manager

# Globals and constants variables.

def parse(source):
    return ElementTree.parse(source)

def tostring(element, encoding='UTF-8', pretty_print=True):
    output = ElementTree.tostring(element, encoding=encoding)
    if pretty_print:
        output = minidom.parseString(output).toprettyxml(encoding=encoding)
    return output

class objectxml(object):

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        return cls()

    def __savexml__(self, element, *args, **kwargs):
        pass

    @classmethod
    def from_xml(cls, element, *args, **kwargs):
        return XMLIO.from_xml(element, *args, **kwargs)

    def to_xml(self, *args, **kwargs):
        return XMLIO.to_xml(self, *args, **kwargs)

    @classmethod
    def load(cls, source):
        """
        Loads the object from a file-object.
        The file-object must correspond to a XML file where the options were 
        saved.
        
        :arg source: filepath or file-object
        
        :return: loaded object
        """
        self_opened = False
        if not hasattr(source, "read"):
            source = open(source, "rb")
            self_opened = True

        element = parse(source).getroot()
        if self_opened: source.close()

        return cls.from_xml(element)

    def save(self, source, pretty_print=True):
        """
        Saves this object to a file-object.
        The file-object must correspond to a XML file where the options will 
        be saved.
        
        :arg source: filepath or file-object
        :arg validate: whether to validate XML file against the schemas 
            (default: ``True``)
        """
        element = self.to_xml()
        output = tostring(element, pretty_print=pretty_print)

        self_opened = False
        if not hasattr(source, "write"):
            source = open(source, "wb")
            self_opened = True

        source.write(output)

        if self_opened: source.close()

class _XMLIO(Manager):
    def __init__(self):
        Manager.__init__(self)

    def register_namespace(self, prefix, uri):
        """
        Registers a namespace to be used when loading and saving from/to XML.
        
        :arg prefix: prefix of the namespace
        :arg uri: URI of the namespace
        """
        ElementTree.register_namespace(prefix, uri)

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

    def from_xml(self, element, *args, **kwargs):
        """
        Loads an object from a XML element. A :exc:`ValueError` is raised if
        no loader is found for the XML element.
        
        :arg element: XML element
        """
        klass = self.get_class(element.tag)

        return klass.__loadxml__(element, *args, **kwargs)

    def to_xml(self, obj, *args, **kwargs):
        """
        Saves an object as a XML element. A :exc:`ValueError` is raised if
        no saver is found for the object.
        
        :arg obj: object
        """
        tag = self.get_tag(obj.__class__)
        element = Element(tag)

        obj.__savexml__(element, *args, **kwargs)

        return element

XMLIO = _XMLIO()

