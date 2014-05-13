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
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import xml.etree.ElementTree as etree
import xml.dom.minidom as minidom

# Third party modules.

# Local modules.

# Globals and constants variables.

def parse(source):
    return etree.parse(source).getroot()

def tostring(element, encoding='UTF-8', pretty_print=True):
    output = etree.tostring(element, encoding=encoding)
    if pretty_print:
        output = minidom.parseString(output).toprettyxml(encoding=encoding)
    return output
