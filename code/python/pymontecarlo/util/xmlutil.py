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
from lxml.etree import Element

# Local modules.

# Globals and constants variables.

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

class _XMLIO(object):
    def __init__(self):
        self._loaders = {}
        self._savers = {}

    def register(self, tag, klass):
        self.register_loader(tag, klass)
        self.register_saver(tag, klass)

    def register_loader(self, tag, klass):
        if tag in self._loaders and self._loaders.get(tag) != klass:
            raise ValueError, 'A class (%s) is already registered with the tag (%s).' % \
                (self._loaders[tag].__name__, tag)

        if not issubclass(klass, objectxml):
            raise ValueError, 'The class (%s) must be a subclass of objectxml.' % \
                klass.__name__

        self._loaders[tag] = klass

    def register_saver(self, tag, klass):
        if klass in self._savers and self._savers.get(klass) != tag:
            raise ValueError, 'A tag (%s) is already associated with class (%s).' % \
                (self._savers[klass], klass.__name__)

        if not issubclass(klass, objectxml):
            raise ValueError, 'The class (%s) must be a subclass of objectxml.' % \
                klass.__name__

        self._savers[klass] = tag

    def from_xml(self, element, *args, **kwargs):
        tag = element.tag
        if tag not in self._loaders:
            raise ValueError, 'No loader found for element (%s). Please register it first.' % tag
        klass = self._loaders[tag]

        return klass.__loadxml__(element, *args, **kwargs)

    def to_xml(self, obj, *args, **kwargs):
        klass = obj.__class__
        if klass not in self._savers:
            raise ValueError, 'No saver found for class (%s). Please register it first.' % klass

        tag = self._savers[klass]
        element = Element(tag)

        obj.__savexml__(element, *args, **kwargs)

        return element

XMLIO = _XMLIO()
