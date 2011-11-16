#!/usr/bin/env python
"""
================================================================================
:mod:`option` -- Parent of all options classes
================================================================================

.. module:: option
   :synopsis: Parent of all options classes

.. inheritance-diagram:: option

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter
from xml.etree.ElementTree import Element

# Third party modules.

# Local modules.

# Globals and constants variables.

def parse_class(element, choices):
    """
    Returns the class from which the element should be loaded.
    
    :rtype: :class:`XMLObject`
    """
    tags = dict(zip(map(attrgetter("__name__"), choices), choices))
    clasz = tags.get(element.tag)
    if clasz is None:
        raise IOError, "Element '%s' cannot be loaded by this class." % element.tag

    return clasz

def from_xml_choices(element, choices, *args, **kwargs):
    """
    Loads the element from a list of :class:`XMLObject` classes (with the method 
    :meth:`from_xml`).
    
    :return: loaded :class:`XMLObject`
    """
    clasz = parse_class(element, choices)
    return clasz.from_xml(element, *args, **kwargs)

class XMLObject(object):
    def to_xml(self):
        return Element(self.__class__.__name__)
