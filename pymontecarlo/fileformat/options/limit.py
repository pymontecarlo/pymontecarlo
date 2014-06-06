#!/usr/bin/env python
"""
================================================================================
:mod:`limit` -- XML handler for limits
================================================================================

.. module:: limit
   :synopsis: XML handler for limits

.. inheritance-diagram:: pymontecarlo.fileformat.options.limit

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
from pyxray.transition import Transition

# Local modules.
from pymontecarlo.fileformat.xmlhandler import _XMLHandler

from pymontecarlo.options.limit import TimeLimit, ShowersLimit, UncertaintyLimit

# Globals and constants variables.

class TimeLimitXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}timeLimit'
    CLASS = TimeLimit

    def parse(self, element):
        time_s = self._parse_numerical_parameter(element, 'time')
        return TimeLimit(time_s)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)
        self._convert_numerical_parameter(element, obj.time_s, 'time')
        return element

class ShowersLimitXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}showersLimit'
    CLASS = ShowersLimit

    def parse(self, element):
        showers = self._parse_numerical_parameter(element, 'showers')
        return ShowersLimit(showers)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)
        self._convert_numerical_parameter(element, obj.showers, 'showers')
        return element

class UncertaintyLimitXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}uncertaintyLimit'
    CLASS = UncertaintyLimit

    def parse(self, element):
        transitions = []
        for subelement in element.iter('transition'):
            z = int(self._parse_numerical_parameter(subelement, 'z'))
            src = int(self._parse_numerical_parameter(subelement, 'src'))
            dest = int(self._parse_numerical_parameter(subelement, 'dest'))
            transitions.append(Transition(z, src, dest))

        detector_key = self._parse_text_parameter(element, 'detector_key')

        uncertainty = self._parse_numerical_parameter(element, 'uncertainty')

        return UncertaintyLimit(transitions, detector_key, uncertainty)

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        for transition in np.array(obj.transition, ndmin=1):
            subelement = etree.SubElement(element, 'transition')
            subelement.set('z', str(transition.z))
            subelement.set('src', str(transition.src.index))
            subelement.set('dest', str(transition.dest.index))

        self._convert_text_parameter(element, obj.detector_key, 'detector_key')

        self._convert_numerical_parameter(element, obj.uncertainty, 'uncertainty')
        return element
