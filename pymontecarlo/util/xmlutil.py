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
import sys
from xml.etree.ElementTree import Element

# Third party modules.

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
        module, name = element.tag.rsplit('.', 1)

        # This import technique is the same as the one used in pickle
        # See Unpickler.find_class
        __import__(module)
        mod = sys.modules[module]
        klass = getattr(mod, name)

        return klass.__loadxml__(element, *args, **kwargs)

    def to_xml(self, *args, **kwargs):
        name = self.__class__.__module__ + "." + self.__class__.__name__
        element = Element(name)

        self.__savexml__(element, *args, **kwargs)

        return element

