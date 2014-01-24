#!/usr/bin/env python
"""
================================================================================
:mod:`xmlhandler` -- Handler to convert/parse to/from XML
================================================================================

.. module:: xmlhandler
   :synopsis: Handler to convert/parse to/from XML

.. inheritance-diagram:: pymontecarlo.fileformat.xmlhandler

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import xml.etree.ElementTree as etree

# Third party modules.

import numpy as np

# Local modules.
from pymontecarlo.fileformat.handler import _Handler

# Globals and constants variables.

class _XMLHandler(_Handler):

    TAG = None
    CLASS = None

    def can_parse(self, element):
        return element.tag == self.TAG

    def parse(self, element):
        return self.CLASS()

    def _parse_text_parameter(self, element, attrib_name=None, required=True):
        if required and attrib_name is not None and attrib_name not in element.attrib:
            raise ValueError("Attribute '%s' not found" % attrib_name)

        if attrib_name is None:
            text = element.text
        else:
            text = element.get(attrib_name)

        return np.array(text.split(','), 'U')

    def _parse_numerical_parameter(self, element, attrib_name=None, required=True):
        values = self._parse_text_parameter(element, attrib_name, required)
        return np.array(values, np.float)

    def _parse_bool_parameter(self, element, attrib_name=None, required=True):
        values = self._parse_text_parameter(element, attrib_name, required)

        newvalues = []
        for value in values:
            if value == 'true':
                newvalues.append(True)
            elif value == 'false':
                newvalues.append(False)
            else:
                raise ValueError('Incorrect boolean value: %s' % value)

        return np.array(newvalues, '?')

    def convert(self, obj):
        return etree.Element(self.TAG)

    def _convert_text_parameter(self, element, values, attrib_name=None):
        values = np.array(values, ndmin=1)
        for value in values:
            if ',' in str(value):
                raise ValueError('"," in value')
        text = ','.join(map(str, values))

        if attrib_name is None:
            element.text = text
        else:
            element.set(attrib_name, text)

    def _convert_numerical_parameter(self, element, values, attrib_name=None):
        values = np.array(values, 'U')
        self._convert_text_parameter(element, values, attrib_name)

    def _convert_bool_parameter(self, element, values, attrib_name=None):
        newvalues = []
        for value in np.array(values, '?', ndmin=1):
            newvalues.append('true' if value else 'false')
        self._convert_text_parameter(element, newvalues, attrib_name)
