#!/usr/bin/env python
"""
================================================================================
:mod:`options` -- XML handler for options
================================================================================

.. module:: options
   :synopsis: XML handler for options

.. inheritance-diagram:: pymontecarlo.fileformat.options.options

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
from pymontecarlo.fileformat.xmlhandler import _XMLHandler
from pymontecarlo.fileformat.handler import \
    find_convert_handler, find_parse_handler

from pymontecarlo.options.options import Options

import pymontecarlo.util.xmlutil as xmlutil

# Globals and constants variables.

def load(source):
    element = xmlutil.parse(source)
    handler = find_parse_handler('pymontecarlo.fileformat.options.options', element)
    return handler.parse(element)

def save(options, dest):
    handler = find_convert_handler('pymontecarlo.fileformat.options.options', options)
    element = handler.convert(options)
    output = xmlutil.tostring(element)

    self_opened = False
    if not hasattr(dest, "write"):
        dest = open(dest, "wb")
        self_opened = True
    dest.write(output)
    if self_opened: dest.close()

class OptionsXMLHandler(_XMLHandler):

    TAG = '{http://pymontecarlo.sf.net}options'
    CLASS = Options
    VERSION = '7'

    def parse(self, element):
        version = element.attrib['version']
        if version != self.VERSION:
            raise ValueError('Incompatible version: %s != %s' % \
                             (version, self.VERSION))

        name = element.attrib['name']
        obj = Options(name)

        obj._uuid = element.attrib['uuid']

        subelement = element.find('beam')
        if subelement is None:
            raise ValueError("Element 'beam' not found")
        beams = []
        for subsubelement in subelement:
            beams.append(self._parse_handlers('pymontecarlo.fileformat.options.beam', subsubelement))
        obj.beam = beams

        subelement = element.find('geometry')
        if subelement is None:
            raise ValueError("Element 'geometry' not found")
        geometries = []
        for subsubelement in subelement:
            geometries.append(self._parse_handlers('pymontecarlo.fileformat.options.geometry', subsubelement))
        obj.geometry = geometries

        subelement = element.find('detectors')
        if subelement is None:
            raise ValueError("Element 'detectors' not found")
        detectors = {}
        for subsubelement in subelement:
            key = subsubelement.attrib['_key']
            detector = self._parse_handlers('pymontecarlo.fileformat.options.detector', subsubelement)
            detectors.setdefault(key, []).append(detector)
        obj.detectors.update(detectors)

        subelement = element.find('limits')
        if subelement is None:
            raise ValueError("Element 'limits' not found")
        for subsubelement in subelement:
            obj.limits.add(self._parse_handlers('pymontecarlo.fileformat.options.limit', subsubelement))

        subelement = element.find('models')
        if subelement is None:
            raise ValueError("Element 'models' not found")
        for subsubelement in subelement:
            obj.models.add(self._parse_handlers('pymontecarlo.fileformat.options.model', subsubelement))

        return obj

    def convert(self, obj):
        element = _XMLHandler.convert(self, obj)

        element.set('version', self.VERSION)
        element.set('name', obj.name)
        element.set('uuid', obj._uuid or 'xsi:nil')

        subelement = etree.SubElement(element, 'beam')
        for beam in np.array(obj.beam, ndmin=1):
            subelement.append(self._convert_handlers('pymontecarlo.fileformat.options.beam', beam))

        subelement = etree.SubElement(element, 'geometry')
        for geometry in np.array(obj.geometry, ndmin=1):
            subelement.append(self._convert_handlers('pymontecarlo.fileformat.options.geometry', geometry))

        subelement = etree.SubElement(element, 'detectors')
        for key, detectors in obj.detectors.items():
            for detector in np.array(detectors, ndmin=1):
                subsubelement = self._convert_handlers('pymontecarlo.fileformat.options.detector', detector)
                subsubelement.set('_key', key)
                subelement.append(subsubelement)

        subelement = etree.SubElement(element, 'limits')
        for limit in obj.limits:
            subelement.append(self._convert_handlers('pymontecarlo.fileformat.options.limit', limit))

        subelement = etree.SubElement(element, 'models')
        for model in obj.models:
            subelement.append(self._convert_handlers('pymontecarlo.fileformat.options.model', model))

        return element
